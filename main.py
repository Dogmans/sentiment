# main.py
import os
import csv
from datetime import datetime
from dataclasses import asdict
from twitter_article_retrieval import TwitterArticleRetrieval
from reddit_article_retrieval import RedditArticleRetrieval
from web_article_retrieval import WebArticleRetrieval
from rss_article_retrieval import RSSArticleRetrieval
from article_retrieval import ArticleRetrieval
from stocks import get_sp500_stocks, StockData
from typing import Dict, List, Sequence

def process_stocks(stocks: Dict[str, StockData], retrieval_classes: Sequence[ArticleRetrieval]):
    """Process stocks and analyze sentiment"""
    total_stocks = len(stocks)
    processed = 0

    for symbol, stock_data in stocks.items():
        processed += 1
        print(f"Processing {symbol} ({processed}/{total_stocks})")
        
        for retrieval_class in retrieval_classes:
            stock_data.fetch_and_append_articles(retrieval_class)

def main():
    # TODO - add and test other retrieval classes
    retrieval_classes = [
        RSSArticleRetrieval('https://finance.yahoo.com/news/rssindex'),
        RSSArticleRetrieval('http://feeds.marketwatch.com/marketwatch/topstories/'),
        RSSArticleRetrieval('https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'),
        RSSArticleRetrieval('https://www.msn.com/en-us/money/rss'),
    ]

    # Get stock data
    # TODO - add sector etc.
    stocks = get_sp500_stocks()

    # Process stocks
    process_stocks(stocks, retrieval_classes)

    # Write results to CSV
    current_date = datetime.now().date().isoformat()
    csv_file = 'sentiment_results.csv'
    file_exists = os.path.isfile(csv_file)

    if stocks:
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Date'] + list(asdict(next(iter(stocks.values()))).keys()))
            
            for symbol, stock_data in stocks.items():
                writer.writerow([current_date] + list(asdict(stock_data).values()))
                print(f"Symbol: {stock_data.symbol}, Company: {stock_data.company_name}, Average Sentiment: {stock_data.average_sentiment}, Results: {stock_data.sentiment_count}")

if __name__ == "__main__":
    main()
