import trader
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt


def calculate_average(prices):
    return sum(prices) / len(prices)


class BollingerTrader(trader.Trader):
    def __init__(self, balance, init_date, days, window, std_devs):
        self.data = {}
        self.holdings = {}
        self.balance = balance
        self.start = dt.date.fromisoformat(init_date)
        self.days = days
        deltas = [dt.timedelta(days=x) for x in range(self.days)]
        self.date_range = [self.start + delta for delta in deltas]
        self.window = window
        self.standard_deviations = std_devs

    def moving_averages(self, pandas_series):
        return pandas_series.rolling(window=self.window).std()

    def moving_std_dev(self, pandas_series):
        return pandas_series.rolling(window=self.window).mean()

    def convert_to_pandas_series(self):
        if self.check_data(self.asx_code) == 1:
            self.add_data(self.asx_code)

        raw_data = self.data[self.asx_code]["Time Series (Daily)"]
        open_prices = []
        for i in raw_data.keys():
            open_prices.append(float(raw_data[i]["1. open"]))
        return pd.Series(data=open_prices, dtype="float")

    def create_bands(self):
        open_price_series = self.convert_to_pandas_series()
        open_mov_avg = self.moving_averages(open_price_series)
        open_mov_std_dev = self.moving_std_dev(open_price_series)
        upper = open_mov_avg + self.standard_deviations * open_mov_std_dev
        lower = open_mov_avg - self.standard_deviations * open_mov_std_dev
        return upper.tolist(), lower.tolist()

    def plot_bands(self):
        fig, ax = plt.subplots(1, 1)
        upper, lower = self.create_bands()
        dates = list(self.data[self.asx_code]["Time Series (Daily)"].keys())
        ax.plot(dates, self.convert_to_pandas_series())
        ax.fill_between(dates, lower, upper, color="grey")
        ax.set_xticks([x for idx, x in enumerate(dates) if idx % 10 == 0])
        plt.xticks(rotation=70)
        plt.show()

