# main.py
import os
import csv
from datetime import datetime
from dataclasses import asdict
from sentiment_analysis import TwitterSentiment, RedditSentiment, WebScrapingSentiment, RSSFeedSentiment
from stocks import get_sp500_stocks

def process_stocks(stocks, sentiment_classes):
    """Process stocks and analyze sentiment"""
    total_stocks = len(stocks)
    processed = 0

    for symbol, stock_data in stocks.items():
        processed += 1
        print(f"Processing {symbol} ({processed}/{total_stocks})")
        
        for sentiment_class in sentiment_classes:
            results = sentiment_class.fetch_and_analyze(stock_data)
            for text, sentiment in results:
                stock_data.total_sentiment += sentiment
                stock_data.sentiment_count += 1

def main():
    sentiment_classes = [
        RSSFeedSentiment('https://finance.yahoo.com/news/rssindex'),
        RSSFeedSentiment('http://feeds.marketwatch.com/marketwatch/topstories/'),
        RSSFeedSentiment('https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'),
        RSSFeedSentiment('https://www.msn.com/en-us/money/rss'),
    ]

    # Get stock data
    stocks = get_sp500_stocks()

    # Process stocks
    process_stocks(stocks, sentiment_classes)

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
