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
        self.save_sentiment_data()

    def save_sentiment_data(self):
        """Save ticker data with sentiment analysis to the database."""
        if not hasattr(self.ticker, 'save_sentiment_data'):
            return
        
        self.ticker.save_sentiment_data(
            sentiment_count=self.sentiment_count,
            average_sentiment=self.average_sentiment
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
