import unittest
import trader
import datetime
from unittest.mock import patch


class TestStock(unittest.TestCase):
    def test_get_data(self):
        bhp = trader.Stock()
        test_data = bhp.get_data("BHP")
        self.assertEqual("BHP", test_data["Meta Data"]["2. Symbol"][:3])


class TestTrader(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_trader = trader.Trader(10000, "2020-01-01", 100)

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
        print(self.sample_trader.data)
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


if __name__ == "__main__":
    unittest.main()
