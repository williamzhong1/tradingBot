import requests
import datetime as dt
import os
import sqlite3
import json

key = os.environ["APIKEY"]
conn = sqlite3.connect("data.sqlite3")
c = conn.cursor()


class Stock:
    def __init__(self):
        self.baseUrl = "https://www.alphavantage.co/query?"
        self.apiKey = str(key)

    def get_update(self, asx_code):
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": asx_code + ".AX",
            "outputsize": "compact",
            "apikey": self.apiKey
        }
        return requests.get(self.baseUrl, params=params).json()

    def get_data(self, asx_code):
        c.execute("""
            CREATE TABLE IF NOT EXISTS asx_data (
                date TEXT,
                asx_code VARCHAR(5),
                data TEXT,
                PRIMARY KEY(date, asx_code)
            )
        """)
        conn.commit()
        c.execute("""
            SELECT * 
            FROM asx_data
            WHERE asx_code = ?
        """, (asx_code,))
        share_data = c.fetchall()
        if len(share_data) == 0:
            r = self.get_update(asx_code)
            c.execute("""
                INSERT INTO asx_data VALUES (?, ?, ?)
            """, (dt.date.today().strftime("%Y-%m-%d"), asx_code, str(r)))
            conn.commit()
            return r
        elif len(share_data) > 0 and dt.date.fromisoformat(share_data[0][0]) != dt.date.today():
            r = self.get_update(asx_code)
            c.execute("""
                DELETE FROM asx_data WHERE date = ? AND asx_code = ?
            """, (share_data[0][0], share_data[0][1]))
            c.execute("""
                INSERT INTO asx_data VALUES (?, ?, ?)
            """, (dt.date.today().strftime("%Y-%m-%d"), asx_code, str(r)))
            conn.commit()
            return r
        else:
            return json.loads(share_data[0][2].replace("\'", "\""))  # Saving to database converted to str


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

    def check_market(self, asx_code, attempted_purchase_date, price):
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
                trading_days = [x for x in trading_days if dt.date.fromisoformat(x) >=
                                dt.date.fromisoformat(attempted_purchase_date)]
                for i in trading_days:
                    prices = self.data[asx_code]["Time Series (Daily)"][i]
                    if float(prices["3. low"]) <= price <= float(prices["2. high"]):
                        return i
                    else:
                        raise KeyError("Cannot transact at {}. Outside high and low price range".format(price))

    def transact(self, asx_code, date, price, quantity):
        if self.check_data(asx_code) == 1:
            self.add_data(asx_code)
        transaction_date = self.check_market(asx_code, date, price)
        transaction = {transaction_date: {
            "price": price,
            "quantity": quantity,
            "order_date": date
        }}
        return transaction_date, transaction

    def brokerage(self, transaction_amount):
        if transaction_amount > 9999.99:
            return transaction_amount * 0.31 / 100
        elif transaction_amount <= 9999.99:
            return 29.95

    def adjust_balance(self, price, quantity):
        self.balance -= price * quantity

    def adjust_holdings(self, asx_code, transaction_date, transaction):
        if self.check_holdings(asx_code) == 1:
            self.holdings[asx_code] = transaction
        else:
            if self.check_holdings(asx_code) == 0 and transaction_date in self.holdings[asx_code].keys():
                self.holdings[asx_code][transaction_date]["price"] = transaction[transaction_date][
                    "price"]
                old_quantity = self.holdings[asx_code][transaction_date]["quantity"]
                if transaction[transaction_date]["quantity"] < 0:
                    new_quantity = old_quantity - transaction[transaction_date]["quantity"]
                else:
                    new_quantity = old_quantity + transaction[transaction_date]["quantity"]
                self.holdings[asx_code][transaction_date]["quantity"] = new_quantity
                self.holdings[asx_code][transaction_date]["order_date"] = transaction[transaction_date]["order_date"]
            else:
                self.holdings[asx_code][transaction_date] = transaction[transaction_date]

    def buy(self, asx_code, date, price, quantity):
        transaction_date, transaction = self.transact(asx_code, date, price, quantity)
        self.adjust_balance(price, quantity)
        self.balance -= self.brokerage(price * quantity)
        self.adjust_holdings(asx_code, transaction_date, transaction)

    def sell(self, asx_code, date, price, quantity):
        transaction_date, transaction = self.transact(asx_code, date, price, -quantity)
        self.adjust_balance(price, quantity)
        self.balance -= self.brokerage(price * quantity)
        self.adjust_holdings(asx_code, transaction_date, transaction)
