# web_sentiment.py
from bs4 import BeautifulSoup
from article import Article
from .article_retrieval import ArticleRetrieval

class WebArticleRetrieval(ArticleRetrieval):
    def __init__(self, domain, requests_per_second=10):
        super().__init__(requests_per_second)
        self.domain = domain

    def fetch_data(self, data) -> List[Article]:
        """Fetch and analyze articles from web search"""
        search_url = f"https://www.google.com/search?q=site:{self.domain}+{data['info']['symbol']}+{data['info']['shortName']}"
        response = self._rate_limited_request(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all search result links
        articles = []
        print(f"\nProcessing web articles for {data['info']['symbol']} from {self.domain}:")
        
        for link in soup.find_all('a'):
            href = link.get('href', '')
            link_text = link.get_text()
            
            # Filter for actual article links
            if href.startswith('http') and self.domain in href:
                # Remove URL arguments
                base_url = href.split('?')[0]
                relevant_chunks = self.get_link_relevant_chunks(href, data['info'])
                if relevant_chunks:
                    print(f"  - {link_text}")
                    articles.append(Article(title=link_text, link=base_url, chunks=relevant_chunks))
        
        if not articles:
            print("  No relevant articles found")
        print(f"  Total articles found: {len(articles)}")
        return articles
