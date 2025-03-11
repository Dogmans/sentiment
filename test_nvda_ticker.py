import unittest
import yfinance as yf

class TestNVDATicker(unittest.TestCase):

    def setUp(self):
        pass

    def test_nvda_ticker(self):
        ticker = yf.Ticker("NVDA")
        self.assertIsNotNone(ticker.info, "No ticker information was returned for NVDA")

if __name__ == '__main__':

    unittest.main()

