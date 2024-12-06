import feedparser
from datetime import datetime
from sentiment_analysis import SentimentAnalysis

class RSSFeedSentiment(SentimentAnalysis):
    def __init__(self, feed_url):
        super().__init__()
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

    def is_relevant_to_stock(self, title, description, stock_data):
        """Check if the article is relevant to the stock using LLM"""
        article_text = f"{title}. {description}"
        return self.is_relevant(article_text, stock_data)

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

    def fetch_data(self, stock_data, count=100):
        entries = self._get_feed_entries()
        relevant_texts = []

        for entry in entries:
            # Check if entry was published today
            if not self.is_published_today(entry.get('published_parsed')):
                continue

            title = entry.get('title', '')
            description = entry.get('description', '')
            
            # Check if article is relevant to the stock using LLM
            if self.is_relevant_to_stock(title, description, stock_data):
                # Combine title and description for sentiment analysis
                full_text = f"{title}. {description}"
                relevant_texts.append(full_text)

            if len(relevant_texts) >= count:
                break

        return relevant_texts
