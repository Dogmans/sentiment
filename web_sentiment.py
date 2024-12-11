# web_sentiment.py
import requests
from bs4 import BeautifulSoup
from sentiment_analysis import SentimentAnalysis
import time

class WebScrapingSentiment(SentimentAnalysis):
    def __init__(self, domain, requests_per_second=10):
        super().__init__(requests_per_second)
        self.search_url_template = 'https://www.bing.com/search?q={query}:site={domain}&freshness=Day'
        self.domain = domain

    def fetch_data(self, stock_data, count=10):
        search_url = self.search_url_template.format(query=stock_data.symbol, domain=self.domain)
        print(f"\nProcessing web articles for {stock_data.symbol} from {self.domain}:")
        response = self._rate_limited_request(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all search result links
        relevant_texts = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            link_text = link.get_text()
            
            # Filter for actual article links and relevant content
            if href.startswith('http') and self.domain in href: 
                relevant_chunks = self.get_link_relevant_chunks(href, stock_data)
                if relevant_chunks:
                    print(f"  - {link_text}")
                    relevant_texts.extend(relevant_chunks)
        
        if not relevant_texts:
            print("  No relevant articles found")
        print(f"  Total articles found: {len(relevant_texts)}")
        return relevant_texts
