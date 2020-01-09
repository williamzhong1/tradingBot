import requests
import datetime as dt


class Stock:
    def __init__(self):
        self.baseUrl = "https://www.alphavantage.co/query?"
        self.apiKey = ""

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
        self.data[asx_code] = Stock.get_data(asx_code)

    def check_market(self, asx_code, attempted_purchase_date):
        if self.check_data(asx_code) == 1:
            raise Exception("Data for {} is missing. Retrieve data first by calling ADD DATA method".format(asx_code))
        else:
            if dt.date.fromisoformat(attempted_purchase_date) not in self.date_range:
                raise Exception("Date for trade outside parameters.")
            else:
                for i in self.date_range:
                    prices = self.data[asx_code]["Time Series (Daily)"][str(i)]
                    if float(prices["3. low"]) <= attempted_purchase_date <= float(prices["2. high"]):
                        return str(i)

    def buy(self, asx_code, date, purchase_price, quantity):
        if self.check_data(asx_code) == 1:
            self.add_data(asx_code)
        transaction_date = self.check_market(asx_code, date)
        if self.balance >= purchase_price * quantity:
            transaction = {transaction_date: {
                "purchase price": purchase_price,
                "quantity": quantity,
                "order_date": date
            }}
        self.balance -= purchase_price * quantity
        if self.check_holdings(asx_code) == 1:
            self.holdings[asx_code] = transaction
        else:
            current_holdings = self.holdings[asx_code]
            current_holdings[date] = transaction
            self.holdings.update(current_holdings)


BHP = Stock()
print(BHP.get_data("BHP"))