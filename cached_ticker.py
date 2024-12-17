import yfinance as yf
import json
import sqlite3
from datetime import date
import pandas as pd


class CachedTicker:
    def __init__(self, symbol):
        self.symbol = symbol
        self.db_path = 'ticker_cache.db'
        self.loaded_from_cache = False
        self._init_db()
        self.data = self.load_cached_data() or self.fetch_and_cache_data()

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
                self.loaded_from_cache = True
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

    def save_sentiment_data(self, sentiment_count: int, average_sentiment: float):
        """Save sentiment analysis data to the SQLite database."""
        ticker_data = self.load_cached_data()
        if ticker_data:
            ticker_data['sentiment'] = {
                'count': sentiment_count,
                'average': average_sentiment
            }
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE ticker_cache SET data = ? WHERE symbol = ? AND date = ?',
                    (json.dumps(ticker_data), self.symbol, date.today().isoformat())
                )
                conn.commit()
                self.data = ticker_data