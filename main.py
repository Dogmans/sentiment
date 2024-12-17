# main.py
from stocks import get_sp500_stocks


def main():

    # Get stock data
    stocks = get_sp500_stocks()

    # Write results to DB
    for stock in stocks.values():
        stock.update_sentiment_data()

if __name__ == "__main__":
    main()
