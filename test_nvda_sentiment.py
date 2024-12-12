import unittest
from stocks import StockData
from test_article_retrieval import TestArticleRetrieval

class TestNVDASentiment(unittest.TestCase):
    def setUp(self):
        self.stock_data = StockData(
            symbol="NVDA",
            company_name="NVIDIA Corporation",
            market_cap="1.2T",
            price="500",
            change="+2.5%",
            revenue="12B"
        )
        self.article_retrieval = TestArticleRetrieval()

    def test_nvda_sentiment(self):
        # Fetch and append articles
        self.stock_data.fetch_and_append_articles(self.article_retrieval)
        
        # Verify we have articles
        self.assertTrue(len(self.stock_data.articles) > 0, "No articles were retrieved for NVDA")
        
        # Test sentiment metrics
        sentiment_score = self.stock_data.average_sentiment
        self.assertIsNotNone(sentiment_score, "Sentiment score should not be None")
        self.assertGreater(sentiment_score, -1, "Sentiment score should be greater than -1")
        self.assertLess(sentiment_score, 1, "Sentiment score should be less than 1")
        
        # Print sentiment information for visibility
        print(f"\nNVDA Sentiment Analysis Results:")
        print(f"Number of articles: {len(self.stock_data.articles)}")
        print(f"Average sentiment: {sentiment_score:.3f}")
        print(f"Total sentiment: {self.stock_data.total_sentiment:.3f}")
        print(f"Sentiment count: {self.stock_data.sentiment_count}")

if __name__ == '__main__':
    unittest.main()
