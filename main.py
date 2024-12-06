# main.py
import os
import csv
from datetime import datetime
from dataclasses import asdict
from sentiment_analysis import TwitterSentiment, RedditSentiment, WebScrapingSentiment
from stocks import get_sp500_stocks

# Define Twitter API credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Define Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

def main():
    # List of sentiment analysis classes
    # sentiment_classes = [
    #     TwitterSentiment(
    #         TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
    #     ),
    #     RedditSentiment(
    #         REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
    #     ),
    #     MotleyFoolSentiment(),
    #     MsnMoneySentiment(),
    #     YahooFinanceSentiment()
    # ]

    sentiment_classes = [
        WebScrapingSentiment('fool.com'),
        WebScrapingSentiment('money.msn.com'),
        WebScrapingSentiment('finance.yahoo.com')
    ]

    # Get stock data
    stocks = get_sp500_stocks()

    # Iterate over the sentiment analysis classes and fetch & analyze data for each stock
    for sentiment_class in sentiment_classes:
        for symbol, stock_data in stocks.items():
            results = sentiment_class.fetch_and_analyze(symbol)
            platform = sentiment_class.__class__.__name__.replace('Sentiment', '')
            for text, sentiment in results:
                stock_data.total_sentiment += sentiment
                stock_data.sentiment_count += 1

    # Write results to CSV
    current_date = datetime.now().date().isoformat()
    csv_file = 'sentiment_results.csv'
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date'] + list(asdict(next(iter(stocks.values()))).keys()))
        
        for symbol, stock_data in stocks.items():
            writer.writerow([current_date] + list(asdict(stock_data).values()))
            print(f"Symbol: {stock_data.symbol}, Company: {stock_data.company_name}, Average Sentiment: {stock_data.average_sentiment}, Results: {stock_data.sentiment_count}")

if __name__ == "__main__":
    main()
