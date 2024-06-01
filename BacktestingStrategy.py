from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import talib
import numpy as np
import yfinance as yf
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import math

startdate = datetime.datetime(2020, 1, 1)
enddate = datetime.datetime(2024, 1, 1)
capital = 10000
stocks = ['MSFT', 'AAPL', 'GOOGL', 'TSLA','JPM']

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
        
    #first we create a dataframe with the conditions while both are true like minterm and mintermr then compare the local minima and while 
    #the local minima makes higher lows then the price should make lower highs    
    def next(self):
        self.FetchData()
        self.SetIndicator()
        self.Fractal1()
        self.Fractal2()
        self.Fractal3()
        self.Fractal4()  
        self.Divergence()
        self.Signal()

        if len(self.data.Close) < 15:  # Ensure we have enough data points
            return -1
        
        for i in range(len(self.data)):
            rsi = self.data['Rsi'].iloc[i]
            price = self.data['Close'].iloc[i]
            bollinger_mid = self.data['BBmid'].iloc[i]

            prev_rsi = self.data['Rsi'].iloc[i-1]
            prev_price = self.data['Close'].iloc[i-1]

        # Bullish divergence
        if rsi < self.lower_bound_rsi and price < bollinger_mid and rsi > prev_rsi and price < prev_price:
            self.position.close()
            self.buy(sl=(self.stlo * price) / 100, tp=(self.tkpr * price) / 100)
        
        # Bearish divergence
        elif rsi > self.upper_bound_rsi and price > bollinger_mid and rsi < prev_rsi and price > prev_price:
            self.position.close()
            self.sell(tp=(self.stlo * price) / 100, sl=(self.tkpr * price) / 100)

for stock in stocks:
    data = Backtesting(stock,startdate,enddate)
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

class Strategy:
    def __init__(self, ticker, startdate, enddate, capital):
        self.ticker = ticker
        self.startdate = startdate
        self.enddate = enddate
        self.capital = capital
        self.data = None

    def FetchData(self):
        self.data = yf.download(self.ticker, start=self.startdate, end=self.enddate)
        self.data.drop('Adj Close', axis=1, inplace=True)
        return self.data

    def SetIndicator(self):
        self.data['Rsi'] = talib.RSI(self.data['Close'], timeperiod=14)
        self.data['BBup'], self.data['BBmid'], self.data['BBlow'] = talib.BBANDS(self.data['Close'], timeperiod=14)
        self.data['VolumeDelta'] = self.data['Volume'].diff()
        return self.data

    def Fractal1(self):
        self.data['minterm'] = False
        for i in range(2, len(self.data) - 2):
            if (self.data['Close'].iloc[i] < self.data['Close'].iloc[i - 1]) & (self.data['Close'].iloc[i] < self.data['Close'].iloc[i - 2]) & (self.data['Close'].iloc[i] < self.data['Close'].iloc[i + 1]) & (self.data['Close'].iloc[i] < self.data['Close'].iloc[i + 2]):
                self.data['minterm'].iloc[i] = True
        return self.data

    def Fractal2(self):
        self.data['maxterm'] = False
        for i in range(2, len(self.data) - 2):
            if (self.data['Close'].iloc[i] > self.data['Close'].iloc[i - 1]) & (self.data['Close'].iloc[i] > self.data['Close'].iloc[i - 2]) & (self.data['Close'].iloc[i] > self.data['Close'].iloc[i + 1]) & (self.data['Close'].iloc[i] > self.data['Close'].iloc[i + 2]):
                self.data['maxterm'].iloc[i] = True
        return self.data

    def Fractal3(self):
        self.data['mintermr'] = False
        for i in range(2, len(self.data) - 2):
            if (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i - 1]) & (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i - 2]) & (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i + 1]) & (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i + 2]):
                self.data['mintermr'].iloc[i] = True
        return self.data

    def Fractal4(self):
        self.data['maxtermr'] = False
        for i in range(2, len(self.data) - 2):
            if (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i - 1]) & (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i - 2]) & (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i + 1]) & (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i + 2]):
                self.data['maxtermr'].iloc[i] = True
        return self.data

    def Divergence(self):
        self.data['DivergenceSignal'] = 0
        for i in range(2, len(self.data) - 1):
            if (self.data['Close'].iloc[i] < self.data['Close'].iloc[i - 1]) & (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i + 1]):
                self.data['DivergenceSignal'].iloc[i] = 1
            if (self.data['Close'].iloc[i] > self.data['Close'].iloc[i - 1]) & (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i + 1]):
                self.data['DivergenceSignal'].iloc[i] = -1
        return self.data

    def Signal(self):
        self.data['Signal'] = 0
        for i in range(len(self.data)):
            if (self.data['Rsi'].iloc[i] < 40) & (self.data['Close'].iloc[i] < (self.data['BBmid'].iloc[i]) / 2) & (self.data['VolumeDelta'].iloc[i] > 0) & (self.data['minterm'].iloc[i] == True) & (self.data['mintermr'].iloc[i] == True):
                self.data['Signal'].iloc[i] = 1
            elif (self.data['Rsi'].iloc[i] > 60) & (self.data['Close'].iloc[i] > (self.data['BBmid'].iloc[i]) / 2) & (self.data['VolumeDelta'].iloc[i] < 0) & (self.data['maxterm'].iloc[i] == True) & (self.data['maxtermr'].iloc[i] == True):
                self.data['Signal'].iloc[i] = -1
        return self.data
        

