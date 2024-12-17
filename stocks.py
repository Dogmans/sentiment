import csv
from dataclasses import dataclass
from datetime import date
import json
import os
import time
from typing import Dict, List

import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, Column, String, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

import article
from retrieval.rss_article_retrieval import RSSArticleRetrieval
from retrieval.ticker_article_retrieval import TickerArticleRetrieval

retrieval_classes = [
    TickerArticleRetrieval(),
    RSSArticleRetrieval('http://feeds.marketwatch.com/marketwatch/topstories/'),
    RSSArticleRetrieval('https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'),
    RSSArticleRetrieval('https://www.msn.com/en-us/money/rss'),
]

Base = declarative_base()

class TickerCache(Base):
    __tablename__ = 'ticker_cache'

    symbol = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    data = Column(JSON)


@dataclass
class Stock:
    symbol: str
    _articles: List[article.Article] = None
    _ticker_data: Dict = None
    db_url: str = 'sqlite:///ticker_cache.db'

    def __post_init__(self):
        self._articles = []
        self._init_db()
        self._ticker_data = self.load_cached_data() or self.fetch_and_cache_data()

    def _init_db(self):
        """Initialize SQLAlchemy engine and create tables if they don't exist."""
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def load_cached_data(self):
        """Load ticker data from database if it exists and is from today."""
        with self.Session() as session:
            result = session.query(TickerCache).filter(
                TickerCache.symbol == self.symbol,
                TickerCache.date == date.today()
            ).first()
            if result:
                return result.data
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
        
        with self.Session() as session:
            cache_entry = TickerCache(
                symbol=self.symbol,
                date=date.today(),
                data=ticker_data
            )
            session.merge(cache_entry)
            session.commit()
        
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
            with self.Session() as session:
                cache_entry = session.query(TickerCache).filter(
                    TickerCache.symbol == self.symbol,
                    TickerCache.date == date.today()
                ).first()
                if cache_entry:
                    cache_entry.data = ticker_data
                    session.commit()
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
