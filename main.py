# main.py
from stocks import get_sp500_stocks, StockData

def main():
    # Get stock data
    stocks = get_sp500_stocks()

    # Write results to CSV
    csv_file = 'sentiment_results.csv'
    for stock in stocks.values():
        stock.write_to_csv(csv_file)
            
if __name__ == "__main__":
    main()
