# sentiment_analysis.py
import requests
from bs4 import BeautifulSoup
from sentiment_analysis import SentimentAnalysis

class WebScrapingSentiment(SentimentAnalysis):
    def __init__(self, domain):
        super().__init__()
        self.search_url_template = 'https://www.bing.com/search?q={query}:site={domain}&freshness=Day'
        self.domain = domain

    def article_link_filter(self, query, link_text):
        # Use the LLM to check if the link text is relevant to the stock query
        prompt = f"Is this headline relevant to {query} stock: {link_text}"
        try:
            analysis = self.sentiment_model(prompt)
            return analysis[0]['label'] == 'POSITIVE'
        except Exception as e:
            print(f"Error analyzing link relevance: {e}")
            # Fall back to basic keyword matching if LLM fails
            relevant_terms = ['stock', 'market', 'invest', query.lower()]
        return any(term in link_text.lower() for term in relevant_terms)

    def fetch_data(self, query, count=10):
        search_url = self.search_url_template.format(query=query, domain=self.domain)
        print("fetching data from", search_url)
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all search result links
        articles = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            link_text = link.get_text()
            
            # Filter for actual article links and relevant content
            if (href.startswith('http') and 
                self.domain in href and 
                self.article_link_filter(query, link_text)):
                
                try:
                    article_response = requests.get(href)
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
