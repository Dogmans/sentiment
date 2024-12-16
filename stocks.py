import requests
from bs4 import BeautifulSoup
from article import Article
from dataclasses import dataclass, field
from typing import Dict, List
import yfinance as yf
import pandas as pd
import time

@dataclass
class StockData:
    symbol: str
    company_name: str
    market_cap: str
    price: str
    change: str
    revenue: str
    sector: str = ""
    articles : List[Article] = field(default_factory=list)

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

    def fetch_and_append_articles(self, retrieval) -> None:
        """Fetch sentiment data and append unique articles"""
        seen_urls = {article.url for article in self.articles}
        new_articles = retrieval.fetch_data(self)
        for article in new_articles:
            if article.url not in seen_urls:
                self.articles.append(article)
                seen_urls.add(article.url)


def get_stock_data(ticker):
    time.sleep(0.1)  # 100ms delay
    stock = yf.Ticker(ticker)
    info = stock.info

    prev_close = info.get('previousClose')
    '''
    current_price = info.get('ask')
    price_change_percent = ((current_price - prev_close) / prev_close) * 100 if prev_close else None
    '''

    return {
        'Ticker': ticker,
        'Company': info.get('shortName'),
        'Sector': info.get('sector'),
        'Industry': info.get('industry'),
        'Market Cap': info.get('marketCap'),
        'Previous Close': prev_close
    }


# TODO - add region
def get_sp500_stocks() -> Dict[str, StockData]:

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    sp500_table = pd.read_html(url)
    sp500_df = sp500_table[0]

    stocks_data = {}
    for symbol in sp500_df['Symbol']:
        stocks_data[symbol] = get_stock_data(symbol)
    
    return stocks_data
