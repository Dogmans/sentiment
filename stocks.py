import csv
from dataclasses import dataclass
from datetime import date
import json
import os
import sqlite3
import time
from typing import Dict, List

import pandas as pd
import yfinance as yf

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
class Stock:
    symbol: str
    _articles: List[article.Article] = None
    _ticker_data: Dict = None
    db_path: str = 'ticker_cache.db'

    def __post_init__(self):
        self._articles = []
        self._init_db()
        self._ticker_data = self.load_cached_data() or self.fetch_and_cache_data()

    def _init_db(self):
        """Initialize SQLite database and create table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticker_cache (
                    symbol TEXT,
                    date TEXT,
                    data TEXT,
                    PRIMARY KEY (symbol, date)
                )
            ''')
            conn.commit()

    def load_cached_data(self):
        """Load ticker data from SQLite if it exists and is from today."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT data FROM ticker_cache WHERE symbol = ? AND date = ?',
                (self.symbol, date.today().isoformat())
            )
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
        return None

    def fetch_and_cache_data(self):
        """Fetch ticker data from Yahoo Finance and cache it in SQLite."""
        ticker = yf.Ticker(self.symbol)
        ticker_data = {
            'info': ticker.info,
            'history': ticker.history(period='1d').to_dict(),
            'news': ticker._news,
            'date': date.today().isoformat()
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO ticker_cache (symbol, date, data) VALUES (?, ?, ?)',
                (self.symbol, date.today().isoformat(), json.dumps(ticker_data))
            )
            conn.commit()
        
        return ticker_data

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
        return len(self.articles)

    def update_sentiment_data(self):
        """Update ticker data with sentiment analysis in the database."""
        ticker_data = self.load_cached_data()
        if ticker_data:
            ticker_data['sentiment'] = {
                'count': self.sentiment_count,
                'average': self.average_sentiment
            }
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE ticker_cache SET data = ? WHERE symbol = ? AND date = ?',
                    (json.dumps(ticker_data), self.symbol, date.today().isoformat())
                )
                conn.commit()
                self._ticker_data = ticker_data

    @property
    def info(self):
        return self._ticker_data['info']

    @property
    def history(self):
        return pd.DataFrame(self._ticker_data['history'])

    @property
    def news(self):
        return self._ticker_data['news']


def get_sp500_stocks() -> Dict[str, Stock]:
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    sp500_table = pd.read_html(url)
    sp500_df = sp500_table[0]

    stocks_data = {}
    for symbol in sp500_df['Symbol']:
        stocks_data[symbol] = Stock(symbol=symbol)
        time.sleep(0.5)  # 500ms delay so we don't hit the rate limit
    
    return stocks_data
