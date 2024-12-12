from transformers import pipeline
import re
import nltk
import time
import requests
from bs4 import BeautifulSoup
import torch
from nltk.tokenize import sent_tokenize
from typing import List
from dataclasses import dataclass
from typing import List, Dict, Tuple
from article import Article
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

class SentimentAnalysis:
    def __init__(self, requests_per_second=10):
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        self.relevance_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",  # One of the best zero-shot classifiers
            device=0 if torch.cuda.is_available() else -1
        )
        self.max_length = 512  # Maximum token length for the model
        self.delay = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0
        self._url_cache = {}  # Cache for URL responses

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
        response = requests.get(url)
        self.last_request_time = time.time()
        
        # Cache the response
        self._url_cache[url] = response
        return response

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

    def analyze_text(self, text):
        """Analyze the sentiment of a text chunk using LLM."""
        if not text:
            return 0
            
        try:
            # Clean the text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Get sentiment - ensure text is a list for batch processing
            results = self.sentiment_pipeline([text])
            if not results:
                return 0
            result = results[0]
            return 1 if result['label'] == 'POSITIVE' else -1
            
        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return 0

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess the input text for relevance checking."""
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text.lower()

    def _extract_company_keywords(self, stock_data) -> List[str]:
        """Extract relevant keywords from company data."""
        keywords = [stock_data.symbol.lower()]
        name_words = stock_data.company_name.lower().split()
        common_words = {'inc', 'corp', 'corporation', 'ltd', 'limited', 'llc', 'company', 'co', 'the'}
        keywords.extend([word for word in name_words if word not in common_words])
        return keywords

    def get_link_relevant_chunks(self, link, stock_data):
        """
        Returns list of relevant text chunks at a given link.
        """
        try:
            # Fetch and parse the full article using cached request
            article_response = self._rate_limited_request(link)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Extract article text from paragraphs
            paragraphs = article_soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])
            
            if article_text:
                return self.extract_relevant_chunks(article_text, stock_data)
                    
        except Exception as e:
            print(f"Error fetching article from {link}: {str(e)}")
            
        return []

    def extract_relevant_chunks(self, text, stock_data):
        """
        Check if the text is relevant to the stock using zero-shot classification.
        Analyzes text in chunks and returns any relevant chunks.
        Returns: List of relevant text chunks, empty list if none are relevant.
        """
        try:
            # First do a quick keyword check for efficiency
            text = self._preprocess_text(text)
            keywords = self._extract_company_keywords(stock_data)
            
            if not any(keyword in text for keyword in keywords):
                return []

            # Split into manageable chunks
            chunks = self.chunk_text(text)
            if not chunks:
                return []

            # Prepare labels for zero-shot classification
            hypothesis_template = "This text is about {}."
            labels = [
                f"{stock_data.company_name} ({stock_data.symbol})",
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

    def fetch_data(self, stock_data):
        """
        Abstract method to be implemented by subclasses.
        Should return a list of relevant articles.
        """
        raise NotImplementedError("Subclasses must implement fetch_data")
