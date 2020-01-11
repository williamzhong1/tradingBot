# Simulated Trading Bot

A python module to test trading strategies against historical ASX data.

## Getting Started

Clone this repository using `git clone https://github.com/williamzhong1/tradingBot.git` or download directly.

To create a simple trader, initialise:
```
import trader

simple_trader = trader.Trader(10000, "2020-01-01", 100)
```
The arguments are `trader.Trader(trading_account_balance, start_date, days_running)`. Here we initialised a trader 
with an account balance of `$10,0000`, which wil start trading `1/1/2020` and will run for `100` days.

You then can tell the trader object to buy or sell. 

```angular2
simple_trader.buy("BHP", "2020-01-02", 40, 10)
``` 
The arguments are `..(asx_code, order_date, purchase_price, quantity)`. So here, we ordered the `simple_trader` to buy
`10` `BHP` shares on the `2/1/2020` at `$40`. If the transaction cannot be completed on the order date, the trader will 
search for the next possible time. A transaction typically could not be completed because the market was not open on 
the desired date, or the share is not purchasable at that price.

An order to sell a share takes similar arguments:

```angular2
simple_trader.sell("BHP", "2020-01-02", 40, 10)
```

You can complete a series of transactions in this way. At any time you may ask for your trader's holdings.

```angular2
simple_trader.holdings
```

Alternatively you may inherit these buy sell methods and build a strategy around that:

`class strategy(trader.Trader)...`

An example for this usage is included in `src/bollingerBandsStrategy.py`.

### Prerequisites

This project depends on the `requests` module which can be installed with `pip` or `conda`.

The project also depends on `sqlite3`, `json` and `datetime` but these should be included in the standard library
and do not need to be installed.

This project also requires an API key which is set an environment variable APIKEY. Alternatively you may open the 
`trader.py` and set the variable in `11` which currently reads `self.apiKey = str(key)` to your API key.

You can obtain an API key from: https://www.alphavantage.co/

