import unittest
import trader
import datetime
from unittest.mock import patch

# Testing Stock class will make API call. Commented out to reduce frequency of API calls.

"""
class TestStock(unittest.TestCase):
    def test_get_data(self):
        bhp = trader.Stock()
        test_data = bhp.get_data("BHP")
        self.assertEqual("BHP", test_data["Meta Data"]["2. Symbol"][:3])
"""

balance = 1000000
start_date = "2020-01-01"
days_run = 100


class TestTrader(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_trader = trader.Trader(balance, start_date, days_run)

    def test_init_datetime_convert(self):
        self.assertIsInstance(self.sample_trader.start, datetime.date)

    @patch("trader.Stock.get_data", return_value={
        'Meta Data': {'1. Information': 'Daily Prices (open, high, low, close) and '
                                        'Volumes',
                      '2. Symbol': 'BHP.AX', '3. Last Refreshed': '2020-01-09',
                      '4. Output Size': 'Compact', '5. Time Zone': 'US/Eastern'},
        'Time Series (Daily)': {
            '2020-01-09': {'1. open': '39.8300', '2. high': '40.2250',
                           '3. low': '39.7900', '4. close': '40.0300',
                           '5. volume': '5272166'}}
    })
    def test_add_data(self, mock_stock_data):
        self.sample_trader.add_data("BHP")
        self.assertEqual(self.sample_trader.data["BHP"]["Meta Data"]["2. Symbol"][:3], "BHP")

    @patch("trader.Stock.get_data", return_value={
        'Meta Data': {'1. Information': 'Daily Prices (open, high, low, close) and '
                                        'Volumes',
                      '2. Symbol': 'BHP.AX', '3. Last Refreshed': '2020-01-09',
                      '4. Output Size': 'Compact', '5. Time Zone': 'US/Eastern'},
        'Time Series (Daily)': {
            '2020-01-09': {'1. open': '39.8300', '2. high': '40.2250',
                           '3. low': '39.7900', '4. close': '40.0300',
                           '5. volume': '5272166'}}
    })
    def test_check_data(self, mock_stock_data):
        self.assertEqual(self.sample_trader.check_data("BHP"), 1)
        self.sample_trader.add_data("BHP")
        self.assertEqual(self.sample_trader.check_data("BHP"), 0)

    def test_check_holdings(self):
        self.assertEqual(self.sample_trader.check_holdings("BHP"), 1)

    @patch("trader.Stock.get_data", return_value={
        'Meta Data': {'1. Information': 'Daily Prices (open, high, low, close) and '
                                        'Volumes',
                      '2. Symbol': 'BHP.AX', '3. Last Refreshed': '2020-01-03',
                      '4. Output Size': 'Compact', '5. Time Zone': 'US/Eastern'},
        'Time Series (Daily)': {
            '2020-01-03': {'1. open': '39.8300', '2. high': '40.2250',
                           '3. low': '39.7900', '4. close': '40.0300',
                           '5. volume': '5272166'}}
    })
    def test_check_market(self, mock_stock_data):
        self.assertRaises(NameError, self.sample_trader.check_market, "BHP", "2020-01-01", 100)
        self.sample_trader.add_data("BHP")
        self.assertRaises(KeyError, self.sample_trader.check_market, "BHP", "2000-01-01", 100)
        self.assertRaises(KeyError, self.sample_trader.check_market, "BHP", "2020-01-03", 100)
        self.assertEqual(self.sample_trader.check_market("BHP", "2020-01-03", 39.80), "2020-01-03")

    @patch("trader.Stock.get_data", return_value={
        'Meta Data': {'1. Information': 'Daily Prices (open, high, low, close) and '
                                        'Volumes',
                      '2. Symbol': 'BHP.AX', '3. Last Refreshed': '2020-01-03',
                      '4. Output Size': 'Compact', '5. Time Zone': 'US/Eastern'},
        'Time Series (Daily)': {
            '2020-01-03': {'1. open': '39.8300', '2. high': '40.2250',
                           '3. low': '39.7900', '4. close': '40.0300',
                           '5. volume': '5272166'},
            '2020-01-04': {'1. open': '20', '2. high': '21',
                           '3. low': '19', '4. close': '40.0300',
                           '5. volume': '5272166'}}
    })
    def test_buy(self, mock_stock_data):
        self.sample_trader.buy("BHP", "2020-01-01", 40, 10)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-03"]["quantity"], 10)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-03"]["price"], 40)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-03"]["order_date"], "2020-01-01")
        self.assertEqual(self.sample_trader.balance, balance - (40 * 10))
        self.sample_trader.buy("BHP", "2020-01-04", 20, 10)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]["quantity"], 10)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]["price"], 20)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]["order_date"], "2020-01-04")
        self.sample_trader.buy("BHP", "2020-01-04", 20.5, 20)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]["price"], 20.5)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]["quantity"], 30)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]["order_date"], "2020-01-04")

    @patch("trader.Stock.get_data", return_value={
        'Meta Data': {'1. Information': 'Daily Prices (open, high, low, close) and '
                                        'Volumes',
                      '2. Symbol': 'BHP.AX', '3. Last Refreshed': '2020-01-03',
                      '4. Output Size': 'Compact', '5. Time Zone': 'US/Eastern'},
        'Time Series (Daily)': {
            '2020-01-03': {'1. open': '39.8300', '2. high': '40.2250',
                           '3. low': '39.7900', '4. close': '40.0300',
                           '5. volume': '5272166'},
            '2020-01-04': {'1. open': '20', '2. high': '50',
                           '3. low': '19', '4. close': '40.0300',
                           '5. volume': '5272166'}}
    })
    def test_sell(self, mock_stock_data):
        self.sample_trader.buy("BHP", "2020-01-01", 40, 10)
        self.sample_trader.sell("BHP", "2020-01-04", 30, 10)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]['quantity'], -10)
        self.sample_trader.buy("BHP", "2020-01-04", 30, 10)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]['quantity'], 0)
        self.sample_trader.buy("BHP", "2020-01-04", 30, 10)
        self.assertEqual(self.sample_trader.holdings["BHP"]["2020-01-04"]['quantity'], 10)


if __name__ == "__main__":
    unittest.main()
