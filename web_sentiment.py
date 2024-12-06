# web_sentiment.py
import requests
from bs4 import BeautifulSoup
from sentiment_analysis import SentimentAnalysis
import time

class WebScrapingSentiment(SentimentAnalysis):
    def __init__(self, domain, requests_per_second=10):
        super().__init__()
        self.search_url_template = 'https://www.bing.com/search?q={query}:site={domain}&freshness=Day'
        self.domain = domain
        self.delay = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0

    def _rate_limited_request(self, url):
        """Make a rate-limited request"""
        # Calculate time since last request
        now = time.time()
        time_since_last = now - self.last_request_time
        
        # If we need to wait to maintain rate limit, do so
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        
        # Make the request and update last request time
        response = requests.get(url)
        self.last_request_time = time.time()
        return response

    def fetch_data(self, stock_data, count=10):
        search_url = self.search_url_template.format(query=stock_data.symbol, domain=self.domain)
        print("fetching data from", search_url)
        response = self._rate_limited_request(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all search result links
        articles = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            link_text = link.get_text()
            
            # Filter for actual article links and relevant content
            if (href.startswith('http') and 
                self.domain in href and 
                self.is_relevant(link_text, stock_data)):
                
                try:
                    article_response = self._rate_limited_request(href)
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    
                    # Extract article text from paragraphs
                    paragraphs = article_soup.find_all('p')
                    article_text = ' '.join([p.get_text() for p in paragraphs])
                    
                    if article_text:  # Only add if we got some text
                        articles.append(article_text)
                        if len(articles) >= count:
                            break
                except:
                    continue  # Skip any articles we can't fetch
        
        return articles
