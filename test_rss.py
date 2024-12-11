from rss_sentiment import RSSFeedSentiment
from stocks import StockData

def test_rss_sentiment():
    # Test with a real financial news RSS feed
    rss_feed = RSSFeedSentiment("https://www.investing.com/rss/news.rss")
    
    # Test with a well-known stock
    test_stock = StockData(
        symbol="AAPL",
        company_name="Apple Inc",
        market_cap="3T",
        price="200",
        change="+1.5%",
        revenue="394.3B"
    )
    
    print(f"\nTesting RSS feed sentiment analysis for {test_stock.symbol}")
    print("-" * 50)
    
    # Fetch only 3 articles for testing
    relevant_texts = rss_feed.fetch_data(test_stock, count=3)
    
    if relevant_texts:
        print("\nAnalyzing sentiment for relevant articles:")
        for i, text in enumerate(relevant_texts, 1):
            sentiment_score = rss_feed.analyze_text(text)
            print(f"\nArticle {i} Sentiment Score: {sentiment_score}")
            # Print a snippet of the article for verification
            print(f"Article snippet: {text[:200]}...")
    else:
        print("No relevant articles found for testing")

if __name__ == "__main__":
    test_rss_sentiment()
