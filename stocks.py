import csv
from dataclasses import dataclass
from datetime import date
import os
import time
from typing import Dict, List

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


class CachedTicker:
    def __init__(self, symbol):
        self.symbol = symbol
        self.filename = f'{symbol}_ticker_data.json'
        self.loaded_from_cache = False
        self.data = self.load_cached_data() or self.fetch_and_cache_data()

    def load_cached_data(self):
        """Load ticker data from cache file if it exists and is from today."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                cached_data = json.load(file)
                cache_date = cached_data.get('date')
                if cache_date == date.today().isoformat():
                    self.loaded_from_cache = True
                    return cached_data
        return None

    def fetch_and_cache_data(self):
        """Fetch ticker data from Yahoo Finance and cache it."""
        ticker = yf.Ticker(self.symbol)
        ticker_data = {
            'info': ticker.info,
            'history': ticker.history(period='1d').to_dict(),
            'news': ticker._news,
            'date': date.today().isoformat()
        }
        with open(self.filename, 'w') as file:
            json.dump(ticker_data, file)
        self.loaded_from_cache = False
        return ticker_data

    @property
    def info(self):
        return self.data['info']

    @property
    def history(self):
        return pd.DataFrame(self.data['history'])

    @property
    def news(self):
        return self.data['news']


@dataclass
class StockData:
    ticker : Ticker = None
    symbol : str = None
    _articles : List[article.Article] = []

    @property
    def articles(self) -> List[article.Article]:
        """Fetch sentiment data and append unique articles"""
        if self._articles:
            return self._articles

        seen_urls = {article.link for article in self._articles}

        for retrieval in retrieval_classes:
            new_articles = retrieval.fetch_data(self)
            for article in new_articles:
                if article.link not in seen_urls:
                    self._articles.append(article)
                    seen_urls.add(article.link)
        
        return self._articles

    @property
    def total_sentiment(self) -> float:
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
        cached_ticker = CachedTicker(symbol)
        stocks_data[symbol] = StockData(symbol=symbol, ticker=cached_ticker)
        if not cached_ticker.loaded_from_cache:
            time.sleep(0.5)  # 500ms delay so we don't hit the rate limit
    
    return stocks_data
