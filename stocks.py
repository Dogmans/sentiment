import requests
from bs4 import BeautifulSoup
from article import Article
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class StockData:
    symbol: str
    company_name: str
    market_cap: str
    price: str
    change: str
    revenue: str
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

# TODO - add sector and region
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
