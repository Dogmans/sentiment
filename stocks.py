import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Dict

@dataclass
class StockData:
    symbol: str
    company_name: str
    market_cap: str
    price: str
    change: str
    revenue: str
    total_sentiment: float = 0
    sentiment_count: int = 0

    @property
    def average_sentiment(self) -> float:
        return round(self.total_sentiment / self.sentiment_count, 3) if self.sentiment_count > 0 else 0

def get_sp500_stocks() -> Dict[str, StockData]:
    url = "https://stockanalysis.com/list/sp-500-stocks/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the main table and extract all data
    stocks_data = {}
    
    main_table = soup.find('table', id='main-table')
    if main_table:
        rows = main_table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 7:  # Ensure we have all columns
                symbol = cols[1].text.strip().upper()
                stocks_data[symbol] = StockData(
                    symbol=symbol,
                    company_name=cols[2].text.strip(),
                    market_cap=cols[3].text.strip(),
                    price=cols[4].text.strip(),
                    change=cols[5].text.strip(),
                    revenue=cols[6].text.strip()
                )
    
    return stocks_data
