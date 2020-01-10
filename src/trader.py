import requests
import datetime as dt
import os

key = os.environ["APIKEY"]


class Stock:
    def __init__(self):
        self.baseUrl = "https://www.alphavantage.co/query?"
        self.apiKey = str(key)

    def get_data(self, asx_code):
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": asx_code + ".AX",
            "outputsize": "compact",
            "apikey": self.apiKey
        }
        return requests.get(self.baseUrl, params=params).json()


class Trader:
    def __init__(self, balance, init_date, days):
        self.data = {}
        self.holdings = {}
        self.balance = balance
        self.start = dt.date.fromisoformat(init_date)
        self.days = days
        deltas = [dt.timedelta(days=x) for x in range(self.days)]
        self.date_range = [self.start + delta for delta in deltas]

    def check_data(self, asx_code):
        if asx_code in self.data.keys():
            return 0
        else:
            return 1

    def check_holdings(self, asx_code):
        if asx_code in self.holdings.keys():
            return 0
        else:
            return 1

    def add_data(self, asx_code):
        stock = Stock()
        self.data[asx_code] = stock.get_data(asx_code)

    def check_market(self, asx_code, attempted_purchase_date, purchase_price):
        if self.check_data(asx_code) == 1:
            raise NameError("Data for {} is missing. Retrieve data first by calling ADD DATA method".format(asx_code))
        else:
            if dt.date.fromisoformat(attempted_purchase_date) not in self.date_range:
                raise KeyError("Date outside date range to initialise trader. Initialise a date including {}".format(
                    attempted_purchase_date))
            else:
                trading_days = set(self.data[asx_code]["Time Series (Daily)"].keys()) & set(
                    x.strftime("%Y-%m-%d") for x in self.date_range)
                trading_days = sorted(trading_days)
                deltas = [dt.date.fromisoformat(x) - dt.date.fromisoformat(attempted_purchase_date) for x in
                          trading_days]
                if attempted_purchase_date not in trading_days:
                    deltas = [x for x in deltas if x >= dt.timedelta(0)]
                    """
                    Only want positive deltas because negative deltas mean the trading date occurred before the 
                    attempted purchase date. Cannot go back in time to perform a trade therefore only positive 
                    time deltas are included.
                    """
                for i in deltas:
                    potential_purchase_date = dt.date.fromisoformat(attempted_purchase_date) + i
                    prices = self.data[asx_code]["Time Series (Daily)"][potential_purchase_date.strftime("%Y-%m-%d")]
                    if float(prices["3. low"]) <= purchase_price <= float(prices["2. high"]):
                        return potential_purchase_date.strftime("%Y-%m-%d")
                    else:
                        raise KeyError("Cannot purchase at {}.".format(purchase_price))

    def buy(self, asx_code, date, purchase_price, quantity):
        if self.check_data(asx_code) == 1:
            self.add_data(asx_code)
        transaction_date = self.check_market(asx_code, date, purchase_price)
        if self.balance >= purchase_price * quantity:
            transaction = {transaction_date: {
                "purchase price": purchase_price,
                "quantity": quantity,
                "order date": date
            }}
        self.balance -= purchase_price * quantity
        if self.check_holdings(asx_code) == 1:
            self.holdings[asx_code] = transaction
        else:
            current_holdings = self.holdings[asx_code]
            current_holdings[date] = transaction
            self.holdings.update(current_holdings)
