import trader
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt


def calculate_average(prices):
    return sum(prices) / len(prices)


class BollingerTrader(trader.Trader):
    def __init__(self, balance, init_date, days, window, std_devs, asx_code, quantity, purchase_threshold):
        self.asx_code = asx_code
        self.data = {}
        self.holdings = {}
        self.balance = balance
        self.start = dt.date.fromisoformat(init_date)
        self.days = days
        deltas = [dt.timedelta(days=x) for x in range(self.days)]
        self.date_range = [self.start + delta for delta in deltas]
        self.window = window
        self.standard_deviations = std_devs
        self.quantity = quantity  # Quantity to purchase every time the price intersects with the band
        self.purchase_threshold = purchase_threshold

    def moving_averages(self, pandas_series):
        return pandas_series.rolling(window=self.window).mean()

    def moving_std_dev(self, pandas_series):
        return pandas_series.rolling(window=self.window).std()

    def convert_to_pandas_series(self):
        if self.check_data(self.asx_code) == 1:
            self.add_data(self.asx_code)

        raw_data = self.data[self.asx_code]["Time Series (Daily)"]
        open_prices = []
        for i in raw_data.keys():
            open_prices.append(float(raw_data[i]["1. open"]))
        return pd.Series(data=open_prices[::-1], dtype="float")  # Index data to reverse order

    def create_bands(self):
        open_price_series = self.convert_to_pandas_series()
        open_mov_avg = self.moving_averages(open_price_series)
        open_mov_std_dev = self.moving_std_dev(open_price_series)
        upper = open_mov_avg.add(open_mov_std_dev.mul(self.standard_deviations)).fillna(method="bfill").round(2)
        lower = open_mov_avg.sub(open_mov_std_dev.mul(self.standard_deviations)).fillna(method="bfill").round(2)
        dates = list(self.data[self.asx_code]["Time Series (Daily)"].keys())[::-1]  # Index data to reverse order
        return upper.tolist(), lower.tolist(), open_mov_avg.tolist(), dates

    def plot_bands_transactions(self):
        fig, ax = plt.subplots(1, 1)
        upper, lower, roll_avg, dates = self.create_bands()
        ax.plot(dates, self.convert_to_pandas_series(), linestyle="--")
        ax.fill_between(dates, lower, upper, color="grey")
        ax.plot(dates, roll_avg)
        ax.set_xticks([x for idx, x in enumerate(dates) if idx % 10 == 0])
        ax.title.set_text(self.asx_code)
        plt.xticks(rotation=70)
        intersect_lower_dates, intersect_lower_price, intersect_upper_dates, intersect_upper_price = \
            self.find_intersection_with_bands()
        ax.scatter(intersect_lower_dates, intersect_lower_price, marker='o', color='g')
        ax.scatter(intersect_upper_dates, intersect_upper_price, marker='o', color='g')
        plt.show()
        return fig, ax

    def find_intersection_with_bands(self):
        upper, lower, roll_avg, dates = self.create_bands()
        open_prices = self.convert_to_pandas_series().tolist()
        intersect_upper_price, intersect_upper_dates = [], []
        intersect_lower_price, intersect_lower_dates = [], []
        for idx, i in enumerate(open_prices):
            if upper[idx] - self.purchase_threshold <= i <= upper[idx] + self.purchase_threshold:
                intersect_upper_price.append(i)
                intersect_upper_dates.append(dates[idx])
            elif lower[idx] - self.purchase_threshold <= i <= lower[idx] + self.purchase_threshold:
                intersect_lower_price.append(i)
                intersect_lower_dates.append(dates[idx])
            else:
                continue
        return intersect_lower_dates, intersect_lower_price, intersect_upper_dates, intersect_upper_price

    def make_transactions(self):
        intersect_lower_dates, intersect_lower_price, intersect_upper_dates, intersect_upper_price = \
            self.find_intersection_with_bands()
        for idx, i in enumerate(intersect_lower_dates):
            self.buy(self.asx_code, i, intersect_lower_price[idx], self.quantity)
        for idx, i in enumerate(intersect_upper_dates):
            self.buy(self.asx_code, i, intersect_upper_price[idx], self.quantity)


def main():
    # Create instance of the trader
    example = BollingerTrader(100000, "2019-09-06", 200, 10, 2, "CBA", 10, 0.1)
    # Make transactions which intersect with the bottom or lower band
    example.make_transactions()
    # Plot transactions points
    example.plot_bands_transactions()
    # Print holdings resulting from these transactions
    print(example.holdings)


if __name__ == "__main__":
    main()
