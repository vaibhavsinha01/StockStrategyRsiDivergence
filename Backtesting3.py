from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import talib
import numpy as np
import yfinance as yf
import datetime

# Define the start and end dates for data fetching
startdate = datetime.datetime(2016, 1, 1)
enddate = datetime.datetime(2024, 1, 1)

# List of stocks to fetch data for
stocks = ['NVDA']

class DataFetcher:
    def __init__(self, startdate, enddate):
        self.startdate = startdate
        self.enddate = enddate

    def FetchData(self, ticker):
        data = yf.download(ticker, start=self.startdate, end=self.enddate,interval='1d')
        data.drop('Adj Close', axis=1, inplace=True)
        return data

def optimfunc(series):
    if series["# Trades"] < 10:
        return -1
    else:
        return series['Equity Final [$]']

class Backtesting(Strategy):
    upper_bound_rsi = 70
    lower_bound_rsi = 30
    rsi_window = 14
    bb_window = 14
    stlo = 97
    tkpr = 110

    def init(self):
        self.daily_rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_window)
        self.bollinger_upper, self.bollinger_middle, self.bollinger_lower = self.I(
            talib.BBANDS, self.data.Close, timeperiod=self.bb_window)
        
    def next(self):
        if len(self.data.Close) < 15:  # Ensure we have enough data points
            return -1

        rsi = self.daily_rsi[-1]
        price = self.data.Close[-1]
        bollinger_mid = self.bollinger_middle[-1]

        prev_rsi = self.daily_rsi[-15]
        prev_price = self.data.Close[-15]

        # Bullish divergence
        if rsi < self.lower_bound_rsi and price < bollinger_mid and rsi > prev_rsi and price < prev_price:
            self.position.close()
            self.buy(sl=(self.stlo * price) / 100, tp=(self.tkpr * price) / 100)
        
        # Bearish divergence
        elif rsi > self.upper_bound_rsi and price > bollinger_mid and rsi < prev_rsi and price > prev_price:
            self.position.close()
            self.sell(tp=(self.stlo * price) / 100, sl=(self.tkpr * price) / 100)

fetcher = DataFetcher(startdate, enddate)
for stock in stocks:
    data = fetcher.FetchData(stock)
    bt = Backtest(data, Backtesting, cash=10000)
    stats = bt.run()
    print(f"Backtest results for {stock}:")
    print(stats)
    bt.plot()
    stats = bt.optimize(
        upper_bound_rsi=range(75,85,5),
        lower_bound_rsi=range(40,45,5),
        rsi_window=range(12,13,1),
        bb_window=range(12,13,1),
        stlo=range(96,97,1),
        tkpr=range(113,114,1),
        maximize=optimfunc,
        constraint=lambda param: param.lower_bound_rsi <= param.upper_bound_rsi
    )
    print(stats)

#works perfectly
