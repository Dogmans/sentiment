import csv
from dataclasses import dataclass
from datetime import date
import os
import time
from typing import Any, Dict, List

import pandas as pd
from yfinance import Ticker

import article
from retrieval.rss_article_retrieval import RSSArticleRetrieval
from retrieval.ticker_article_retrieval import TickerArticleRetrieval

retrieval_classes = [
    TickerArticleRetrieval(),
    RSSArticleRetrieval('http://feeds.marketwatch.com/marketwatch/topstories/'),
    RSSArticleRetrieval('https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'),
    RSSArticleRetrieval('https://www.msn.com/en-us/money/rss'),
]

@dataclass
class StockData:
    ticker : Ticker = None
    symbol : str = None
    articles : List[article.Article] = None

    def _fetch_and_append_articles(self, retrieval: Any) -> None:
        """Fetch sentiment data and append unique articles"""
        if self.articles:
            return
        seen_urls = {article.link for article in self.articles}
        new_articles = retrieval.fetch_data(self)
        for article in new_articles:
            if article.link not in seen_urls:
                self.articles.append(article)
                seen_urls.add(article.link)

    @property
    def total_sentiment(self) -> float:
        for retrieval in retrieval_classes:
            self._fetch_and_append_articles(retrieval)
        return sum(article.sentiment_score for article in self.articles)

    @property
    def average_sentiment(self) -> float:
        if self.sentiment_count == 0:
            return 0
        return round(self.total_sentiment / self.sentiment_count, 3)

    @property
    def sentiment_count(self) -> int:
        # TODO - make articles a property so it always retrieves as needed
        return len(self.articles)

    # Function to write ticker info to CSV
    def write_to_csv(self, filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header
            if not os.path.isfile(filename):
                writer.writerow([
                    "Date", "Symbol", "Company Name", "Market Cap", "Price", 
                    "Previous Close", "Open", "High", "Low", "Volume", "News Title", "News URL",
                    "Sentiment Count", "Average Sentiment"
                ])
            
            # Write subset of ticker info
            info = self.ticker.info

            print(info)

            writer.writerow(
                date.today().isoformat(),
                info.get('symbol'),
                info.get('shortName'),
                info.get('marketCap'),
                info.get('regularMarketPrice'),
                info.get('previousClose'),
                info.get('open'),
                info.get('dayHigh'),
                info.get('dayLow'),
                info.get('volume'),
                self.sentiment_count,
                self.average_sentiment
            )


def get_sp500_stocks() -> Dict[str, StockData]:

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    sp500_table = pd.read_html(url)
    sp500_df = sp500_table[0]

    stocks_data = {}
    for symbol in sp500_df['Symbol']:
        time.sleep(0.5)  # 500ms delay
        stocks_data[symbol] = StockData(symbol=symbol, ticker=Ticker(symbol))
    
    return stocks_data
