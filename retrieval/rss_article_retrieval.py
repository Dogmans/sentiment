from datetime import datetime
from typing import List

import feedparser

from article import Article

from .article_retrieval import ArticleRetrieval

class RSSArticleRetrieval(ArticleRetrieval):
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

    def fetch_data(self, data) -> List[Article]:
        entries = self._get_feed_entries()
        articles = []
        print(f"\nProcessing RSS feed articles for {data['info']['symbol']} from {self.feed_url}:")

        for entry in entries:
            # Check if entry was published today
            if not self.is_published_today(entry.get('published_parsed')):
                continue

            title = entry.get('title', '')
            link = entry.get('link', '')
            # Remove URL arguments
            base_url = link.split('?')[0]
            
            if link:
                relevant_chunks = self.get_link_relevant_chunks(link, data['info'])
                if relevant_chunks:
                    print(f"  - {title}")
                    articles.append(Article(title=title, link=base_url, chunks=relevant_chunks))

        if not articles:
            print("  No relevant articles found")
        print(f"  Total articles found: {len(articles)}")
        return articles
