from typing import List
from datetime import datetime

from article import Article
from .article_retrieval import ArticleRetrieval

class TickerArticleRetrieval(ArticleRetrieval):
    def __init__(self, feed_url=None, requests_per_second=10):
        super().__init__(requests_per_second)
        self._cached_feed = None
        self._cached_entries = None

    def is_published_today(self, published_time):
        """Check if the article was published today"""
        return datetime.fromtimestamp(published_time).date() == datetime.now().date()

    def fetch_data(self, data) -> List[Article]:
        articles = []
        print(f"\nProcessing Ticker feed articles for {data['info']['symbol']}:")

        for entry in data['news']:
            # Check if entry was published today
            if not self.is_published_today(entry.get('providerPublishTime')):
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
