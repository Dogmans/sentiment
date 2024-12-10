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
            link = entry.get('link', '')
            
            # Check if article is relevant to the stock using LLM
            if self.is_relevant_to_stock(title, description, stock_data):
                try:
                    # Fetch and parse the full article using cached request
                    article_response = self._rate_limited_request(link)
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    
                    # Extract article text from paragraphs
                    paragraphs = article_soup.find_all('p')
                    article_text = ' '.join([p.get_text() for p in paragraphs])
                    
                    if article_text:  # Only add if we got some text
                        relevant_texts.append(article_text)
                        if len(relevant_texts) >= count:
                            break
                except Exception as e:
                    print(f"Error fetching article from {link}: {str(e)}")
                    # If we can't fetch the full article, fall back to title + description
                    full_text = f"{title}. {description}"
                    relevant_texts.append(full_text)
                    if len(relevant_texts) >= count:
                        break

        return relevant_texts
