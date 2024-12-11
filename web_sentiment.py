# web_sentiment.py
import requests
from bs4 import BeautifulSoup
from sentiment_analysis import Article, SentimentAnalysis
import time

class WebScrapingSentiment(SentimentAnalysis):
    def __init__(self, domain, requests_per_second=10):
        super().__init__(requests_per_second)
        self.domain = domain

    def fetch_data(self, stock_data):
        """Fetch and analyze articles from web search"""
        search_url = f"https://www.google.com/search?q=site:{self.domain}+{stock_data.symbol}+{stock_data.company_name}"
        response = self._rate_limited_request(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all search result links
        articles = []
        print(f"\nProcessing web articles for {stock_data.symbol} from {self.domain}:")
        
        for link in soup.find_all('a'):
            href = link.get('href', '')
            link_text = link.get_text()
            
            # Filter for actual article links
            if href.startswith('http') and self.domain in href:
                # Remove URL arguments
                base_url = href.split('?')[0]
                relevant_chunks = self.get_link_relevant_chunks(href, stock_data)
                if relevant_chunks:
                    print(f"  - {link_text}")
                    articles.append(Article(title=link_text, url=base_url, chunks=relevant_chunks))
        
        if not articles:
            print("  No relevant articles found")
        print(f"  Total articles found: {len(articles)}")
        return articles
