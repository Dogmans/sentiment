# main.py
import os
import csv
from datetime import datetime
from dataclasses import asdict
from twitter_sentiment import TwitterSentiment
from reddit_sentiment import RedditSentiment
from web_sentiment import WebScrapingSentiment
from rss_sentiment import RSSFeedSentiment
from sentiment_analysis import SentimentAnalysis
from stocks import get_sp500_stocks, StockData
from typing import Dict, List, Sequence

def process_stocks(stocks: Dict[str, StockData], sentiment_classes: Sequence[SentimentAnalysis]):
    """Process stocks and analyze sentiment"""
    total_stocks = len(stocks)
    processed = 0

    for symbol, stock_data in stocks.items():
        processed += 1
        print(f"Processing {symbol} ({processed}/{total_stocks})")
        
        # Keep track of processed URLs to avoid duplicates
        seen_urls = {article.url for article in stock_data.articles}
        
        for sentiment_class in sentiment_classes:
            new_articles = sentiment_class.fetch_data(stock_data)
            # Only add articles with unique URLs
            for article in new_articles:
                if article.url not in seen_urls:
                    stock_data.articles.append(article)
                    seen_urls.add(article.url)

def main():
    sentiment_classes = [
        RSSFeedSentiment('https://finance.yahoo.com/news/rssindex'),
        RSSFeedSentiment('http://feeds.marketwatch.com/marketwatch/topstories/'),
        RSSFeedSentiment('https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'),
        RSSFeedSentiment('https://www.msn.com/en-us/money/rss'),
    ]

    # Get stock data
    # TODO - add sector etc.
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
