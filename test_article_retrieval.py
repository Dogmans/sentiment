from article_retrieval import ArticleRetrieval
from article import Article
from typing import List
from test_articles_data import TEST_ARTICLES

class TestArticleRetrieval(ArticleRetrieval):
    """Test implementation that returns predefined articles about NVIDIA and Apple"""
    
    def __init__(self):
        super().__init__()
        self.test_articles = TEST_ARTICLES

    def fetch_data(self, stock_data) -> List[Article]:
        """Return relevant articles for the given stock after checking content relevance"""
        articles = []
        
        # Get all test articles for all companies
        for symbol, test_articles in self.test_articles.items():
            for title, url, content in test_articles:
                # Use the base class's relevance checking
                relevant_chunks = self.extract_relevant_chunks(content, stock_data)
                if relevant_chunks:
                    articles.append(Article(
                        title=title,
                        url=url,
                        chunks=relevant_chunks
                    ))
        
        return articles
