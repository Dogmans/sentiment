from transformers import pipeline
import re
import nltk
import time
import requests
import torch
from nltk.tokenize import sent_tokenize
from typing import List
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
        """
        Analyze sentiment of text, handling long texts by chunking and averaging.
        Returns a sentiment score between -1 and 1.
        """
        if not text or len(text.strip()) == 0:
            return 0
            
        try:
            # Clean the text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split into manageable chunks
            chunks = self.chunk_text(text)
            
            if not chunks:
                return 0
                
            # Analyze each chunk
            chunk_sentiments = []
            for chunk in chunks:
                result = self.sentiment_pipeline(chunk)[0]
                # Convert POSITIVE/NEGATIVE to numeric score
                score = result['score']
                if result['label'] == 'NEGATIVE':
                    score = -score
                chunk_sentiments.append(score)
            
            # Weight chunks by their length for final sentiment
            total_length = sum(len(chunk.split()) for chunk in chunks)
            weighted_sentiment = sum(
                sentiment * len(chunk.split()) / total_length
                for chunk, sentiment in zip(chunks, chunk_sentiments)
            )
            
            return weighted_sentiment
            
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

    def is_relevant(self, text, stock_data):
        """
        Check if the text is relevant to the stock using zero-shot classification.
        This approach is more flexible and can better understand complex relationships.
        """
        try:
            # First do a quick keyword check for efficiency
            text = self._preprocess_text(text)
            keywords = self._extract_company_keywords(stock_data)
            
            if not any(keyword in text for keyword in keywords):
                return False

            # Prepare text and candidate labels for zero-shot classification
            hypothesis_template = "This text is about {}."
            labels = [
                f"{stock_data.company_name} ({stock_data.symbol})",
                "unrelated company or topic"
            ]
            
            # Use zero-shot classification to determine relevance
            result = self.relevance_pipeline(
                text[:1024],  # Truncate to reasonable length while keeping context
                labels,
                hypothesis_template=hypothesis_template,
                multi_label=False
            )
            
            # Return True if the model is more confident about the company label
            return result['labels'][0] == labels[0] and result['scores'][0] > 0.5
            
        except Exception as e:
            print(f"Error checking relevance: {str(e)}")
            return False

    def fetch_and_analyze(self, stock_data):
        """
        Fetch and analyze sentiment data for a stock.
        Returns list of (text, sentiment_score) tuples.
        """
        texts = self.fetch_data(stock_data)
        results = []
        
        for text in texts:
            if self.is_relevant(text, stock_data):
                sentiment = self.analyze_text(text)
                results.append((text, sentiment))
                
        return results

    def fetch_data(self, stock_data):
        """
        Abstract method to be implemented by subclasses.
        Should return a list of texts to analyze.
        """
        raise NotImplementedError("Subclasses must implement fetch_data")
