import feedparser
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from sentiment_analysis import SentimentAnalysis

class RSSFeedSentiment(SentimentAnalysis):
    def __init__(self, feed_url, requests_per_second=10):
        super().__init__(requests_per_second)
        self.feed_url = feed_url
        self._cached_feed = None
        self._cached_entries = None

    def _get_feed_entries(self):
        """Get feed entries from cache or fetch if not cached"""
        if self._cached_entries is None:
            print(f"Fetching RSS feed from {self.feed_url}")
            self._cached_feed = feedparser.parse(self.feed_url)
            self._cached_entries = self._cached_feed.entries
        return self._cached_entries

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

    def fetch_data(self, stock_data):
        entries = self._get_feed_entries()
        relevant_texts = []
        print(f"\nProcessing RSS feed articles for {stock_data.symbol} from {self.feed_url}:")

        for entry in entries:
            # Check if entry was published today
            if not self.is_published_today(entry.get('published_parsed')):
                continue

            title = entry.get('title', '')
            link = entry.get('link', '')
            relevant_chunks = self.get_link_relevant_chunks(link, stock_data)
            if relevant_chunks:
                print(f"  - {title}")
                relevant_texts.extend(relevant_chunks)

        if not relevant_texts:
            print("  No relevant articles found")
        print(f"  Total relevant chunks found: {len(relevant_texts)}")
        return relevant_texts
