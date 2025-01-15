import re
import time

from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
import torch
from transformers import pipeline

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

class ArticleRetrieval:

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def __init__(self, requests_per_second=10):
        self.relevance_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",  # One of the best zero-shot classifiers
            device=0 if torch.cuda.is_available() else -1
        )
        self.max_length = 512  # Maximum token length for the model
        self.delay = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0
        self._url_cache = {}  # Cache for URL responses
    
    def _is_article_page(self, page_source):
        """
        Use zero-shot classification to determine if the page source is likely an article.
        """
        try:
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            text = ' '.join([p.get_text() for p in soup.find_all('p')])

            # If text is too short, it's unlikely to be an article
            if len(text.split()) < 50:
                return False

            # Use the zero-shot classifier to check relevance
            hypothesis_template = "This text is an article."
            labels = ["article", "non-article"]

            result = self.relevance_pipeline(
                text,
                labels,
                hypothesis_template=hypothesis_template,
                multi_label=False
            )

            # Consider the page an article if the confidence for the "article" label is high enough
            return result['labels'][0] == "article" and result['scores'][0] > 0.7

        except Exception as e:
            print(f"Error determining article status: {str(e)}")
            return False


    def _rate_limited_request(self, url):
        """Make a rate-limited request with caching"""
        # Check cache first
        if url in self._url_cache:
            return self._url_cache[url]

        # Calculate time since last request
        now = time.time()
        time_since_last = now - self.last_request_time
        
        # If we need to wait to maintain rate limit, do so
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        
        # Make the request and update last request time
        self.driver.get(url)
        page_source = self.driver.page_source
        self.last_request_time = time.time()
        
        # Use relevance pipeline to check if the page looks like an article
        if not self._is_article_page(page_source):
            input("CAPTCHA detected. Please complete the CAPTCHA and press Enter to continue...")
            page_source = self.driver.page_source
        
        # Cache the response
        self._url_cache[url] = page_source
        return page_source

    def chunk_text(self, text):
        """
        Intelligently chunk text into segments that respect sentence boundaries
        while staying under the max token length.
        """
        # First split into sentences
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            # Rough estimate of tokens (words + punctuation)
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length <= self.max_length:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess the input text for relevance checking."""
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text.lower()

    def get_link_relevant_chunks(self, link, info):
        """
        Returns list of relevant text chunks at a given link.
        """
        try:
            # Fetch and parse the full article using cached request
            page_source = self._rate_limited_request(link)
            article_soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract article text from paragraphs
            paragraphs = article_soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])
            
            if article_text:
                return self.extract_relevant_chunks(article_text, info)
                    
        except Exception as e:
            print(f"Error fetching article from {link}: {str(e)}")
            
        return []

    def extract_relevant_chunks(self, text, info):
        """
        Check if the text is relevant to the stock using zero-shot classification.
        Analyzes text in chunks and returns any relevant chunks.
        Returns: List of relevant text chunks, empty list if none are relevant.
        """
        try:
            # First do a quick keyword check for efficiency
            text = self._preprocess_text(text)

            # Split into manageable chunks
            chunks = self.chunk_text(text)
            if not chunks:
                return []

            # Prepare labels for zero-shot classification
            hypothesis_template = "This text is about {}."
            labels = [
                f"{info.shortName} ({info.symbol})",
                "unrelated company or topic"
            ]
            
            relevant_chunks = []
            # Check each chunk for relevance
            for chunk in chunks:
                result = self.relevance_pipeline(
                    chunk,
                    labels,
                    hypothesis_template=hypothesis_template,
                    multi_label=False
                )
                
                # If chunk is confidently relevant, add it to the list
                if result['labels'][0] == labels[0] and result['scores'][0] > 0.7:
                    relevant_chunks.append(chunk)
            
            return relevant_chunks
            
        except Exception as e:
            print(f"Error checking relevance: {str(e)}")
            return []

    def fetch_data(self, data):
        """
        Abstract method to be implemented by subclasses.
        Should return a list of relevant articles.
        """
        raise NotImplementedError("Subclasses must implement fetch_data")
