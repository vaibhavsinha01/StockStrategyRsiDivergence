import yfinance as yf
import talib
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from backtesting import Backtest, Strategy
import datetime


capital = 10000
startdate = datetime.datetime(2016, 1, 1)
enddate = datetime.datetime(2024, 1, 1)
stocks = ['NVDA','MSFT','AAPL','GOOGL','META']

def optimfunc(series):
    if series["# Trades"] < 10:
        return -1
    else:
        return series['Equity Final [$]']

class Strategy:
    def __init__(self, ticker, startdate, enddate, capital):
        self.ticker = ticker
        self.startdate = startdate
        self.enddate = enddate
        self.capital = capital
        self.data = None

    def fetch_data(self):
        self.data = yf.download(self.ticker, start=self.startdate, end=self.enddate)
        self.data.drop('Adj Close', axis=1, inplace=True)
        return self.data

    def set_indicator(self):
        self.data['Rsi'] = talib.RSI(self.data['Close'], timeperiod=14)
        self.data['BBup'], self.data['BBmid'], self.data['BBlow'] = talib.BBANDS(self.data['Close'], timeperiod=14)
        return self.data

    def fractal1(self):
        self.data['minterm'] = False
        n = 2
        for i in range(2, len(self.data) - 2):
            if all(self.data['Close'].iloc[i] < self.data['Close'].iloc[i - j] and self.data['Close'].iloc[i] < self.data['Close'].iloc[i + j] for j in range(n)):
                self.data['minterm'].iloc[i] = True
        return self.data

    def fractal2(self):
        self.data['mintermr'] = False
        n = 2
        for i in range(2, len(self.data) - 2):
            if all(self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i - j] and self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i + j] for j in range(n)):
                self.data['mintermr'].iloc[i] = True
        return self.data

    def fractal3(self):
        self.data['maxterm'] = False
        n = 2
        for i in range(2, len(self.data) - 2):
            if all(self.data['Close'].iloc[i] > self.data['Close'].iloc[i - j] and self.data['Close'].iloc[i] > self.data['Close'].iloc[i + j] for j in range(n)):
                self.data['maxterm'].iloc[i] = True
        return self.data

    def fractal4(self):
        self.data['maxtermr'] = False
        n = 2
        for i in range(2, len(self.data) - 2):
            if all(self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i - j] and self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i + j] for j in range(n)):
                self.data['maxtermr'].iloc[i] = True
        return self.data

    def divergence(self, data):
        data['DivergenceSignal'] = 0
        n = 3
        for i in range(2, len(data) - n):
            for j in range(1, n + 1):
                if data['Close'].iloc[i] < data['Close'].iloc[i - j] and data['Rsi'].iloc[i] > data['Rsi'].iloc[i + j]:
                    data['DivergenceSignal'].iloc[i] = 1
                elif data['Close'].iloc[i] > data['Close'].iloc[i - j] and data['Rsi'].iloc[i] < data['Rsi'].iloc[i + j]:
                    data['DivergenceSignal'].iloc[i] = -1
        return data

    def signal1(self, data):
        data['Signal1'] = 0
        for i in range(len(data)):
            if data['DivergenceSignal'].iloc[i] == 1 and data['Rsi'].iloc[i] < 50 and data['BBmid'].iloc[i] > data['Close'].iloc[i]:
                data['Signal1'].iloc[i] = 1
        return data

    def signal2(self, data):
        data['Signal2'] = 0
        for i in range(len(data)):
            if data['DivergenceSignal'].iloc[i] == -1 and data['Rsi'].iloc[i] > 50 and data['BBmid'].iloc[i] < data['Close'].iloc[i]:
                data['Signal2'].iloc[i] = -1
        return data

    def apply_conditions(self):
        self.fetch_data()
        self.set_indicator()
        self.fractal1()
        self.fractal2()
        self.fractal3()
        self.fractal4()
        
        fractal_df1 = self.data[(self.data['minterm'] == True) & (self.data['mintermr'] == True)]
        fractal_df2 = self.data[(self.data['maxterm'] == True) & (self.data['maxtermr'] == True)]
        
        divergence_df1 = self.divergence(fractal_df1)
        divergence_df2 = self.divergence(fractal_df2)
        
        self.signal1(divergence_df1)
        self.signal2(divergence_df2)

class Test(Strategy):
    upper_bound_rsi = 70
    lower_bound_rsi = 30
    rsi_window = 14
    bb_window = 14
    stlo = 97
    tkpr = 110

    def init(self):
        ticker = self.data.index.name
        data_with_signals = self.apply_conditions()
        if data_with_signals is None:
            return -1
        return data_with_signals

    def next(self):
        if len(self.data['Close']) < 15:
            return -1
        price = self.data['Close']

        if self.data['Signal'] == 1:
            self.position.close()
            self.buy(sl=(self.stlo * price) / 100, tp=(self.tkpr * price) / 100)
        elif self.data['Signal'] == -1:
            self.position.close()
            self.sell(tp=(self.stlo * price) / 100, sl=(self.tkpr * price) / 100)

def main():
    for ticker in stocks:
        strategy = Strategy(ticker, startdate, enddate, capital)
        data_with_signals = strategy.apply_conditions()
        
        if data_with_signals is None:
            print(f"No data available for {ticker}. Skipping...")
            continue

        # Backtest with MyStrategy
        bt = Backtest(data_with_signals, Test, cash=capital)
        stats = bt.run()
        print(f"Backtest results for {ticker}:")
        print(stats)
        bt.plot()

        # Optimization
        stats = bt.optimize(
            upper_bound_rsi=range(75, 85, 5),
            lower_bound_rsi=range(40, 45, 5),
            rsi_window=range(12, 13, 1),
            bb_window=range(12, 13, 1),
            stlo=range(96, 97, 1),
            tkpr=range(113, 114, 1),
            maximize=optimfunc,
            constraint=lambda param: param.lower_bound_rsi <= param.upper_bound_rsi
        )
        print(stats)

if __name__ == "__main__":
    main()
