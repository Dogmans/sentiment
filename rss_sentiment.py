from transformers import pipeline
import feedparser
from datetime import datetime, timedelta
import re
from sentiment_analysis import SentimentAnalysis

class RSSFeedSentiment(SentimentAnalysis):
    def __init__(self, feed_url):
        super().__init__()
        self.feed_url = feed_url

    def is_relevant_to_stock(self, title, description, symbol):
        """Check if the article is relevant to the stock symbol"""
        search_pattern = re.compile(f'\\b{symbol}\\b', re.IGNORECASE)
        return (search_pattern.search(title) is not None or 
                search_pattern.search(description) is not None)

    def is_published_today(self, published_time):
        """Check if the article was published today"""
        if not published_time:
            return False
        
        try:
            pub_date = datetime(*published_time[:6])
            today = datetime.now().date()
            return pub_date.date() == today
        except (TypeError, ValueError):
            return False

    def fetch_data(self, symbol, count=100):
        feed = feedparser.parse(self.feed_url)
        relevant_texts = []

        for entry in feed.entries:
            # Check if entry was published today
            if not self.is_published_today(entry.get('published_parsed')):
                continue

            title = entry.get('title', '')
            description = entry.get('description', '')
            
            # Check if article is relevant to the stock
            if self.is_relevant_to_stock(title, description, symbol):
                # Combine title and description for sentiment analysis
                full_text = f"{title}. {description}"
                relevant_texts.append(full_text)

            if len(relevant_texts) >= count:
                break

        return relevant_texts
