import yfinance as yf
import json
import os
from datetime import date
import pandas as pd


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