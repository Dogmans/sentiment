from transformers import pipeline
import re

class SentimentAnalysis:
    def __init__(self):
        self.sentiment_model = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

    def is_relevant(self, text, stock_data):
        """Check if the text is relevant to the stock using LLM with regex fallback
        
        Args:
            text (str): The text to analyze (article content, headline, etc.)
            stock_data: StockData object containing symbol and company name
        
        Returns:
            bool: True if the text is relevant to the stock
        """
        prompt = f"Is this article relevant to {stock_data.company_name} ({stock_data.symbol}) stock: {text}"
        try:
            analysis = self.sentiment_model(prompt)
            return analysis[0]['label'] == 'POSITIVE'
        except Exception as e:
            print(f"Error analyzing relevance: {e}")
            # Fall back to basic keyword matching if LLM fails
            patterns = [
                re.compile(f'\\b{stock_data.symbol}\\b', re.IGNORECASE),
                re.compile(f'\\b{stock_data.company_name}\\b', re.IGNORECASE)
            ]
            return any(pattern.search(text) is not None for pattern in patterns)

    def fetch_and_analyze(self, stock_data, count=100):
        """Fetch and analyze sentiment data for a stock
        
        Args:
            stock_data: StockData object containing stock information
            count (int): Maximum number of items to analyze
        """
        data = self.fetch_data(stock_data, count)
        sentiments = []
        for text in data:
            analysis = self.sentiment_model(text[:512])  # Truncate to max length
            sentiments.append((text, 1 if analysis[0]['label'] == 'POSITIVE' else -1))
        return sentiments

    def fetch_data(self, stock_data, count):
        raise NotImplementedError("Subclasses should implement this method")
