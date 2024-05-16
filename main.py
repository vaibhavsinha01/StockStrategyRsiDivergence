import yfinance as yf
import talib
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
capital = 10000
startdate = datetime.datetime(2021, 1, 1)
enddate = datetime.datetime(2024, 1, 1)

stocks = [
    'NVDA','MSFT'
]

class Strategy:
    def FetchData(ticker):
        data = yf.download(ticker, start=startdate, end=enddate)
        data.drop('Adj Close', axis=1, inplace=True)
        return data

    def SetIndicator(data):
        data['Rsi'] = talib.RSI(data['Close'], timeperiod=14)
        data['BBup'], data['BBmid'], data['BBlow'] = talib.BBANDS(data['Close'], timeperiod=14)
        data['VolumeDelta'] = data['Volume'].diff()
        return data

    def Fractal1(data):
        data['minterm'] = False
        for i in range(2, len(data) - 2):
            if (data['Close'].iloc[i] < data['Close'].iloc[i - 1]) & (data['Close'].iloc[i] < data['Close'].iloc[i - 2]) & (data['Close'].iloc[i] < data['Close'].iloc[i + 1]) & (data['Close'].iloc[i] < data['Close'].iloc[i + 2]):
                data['minterm'].iloc[i] = True
        return data

    def Fractal2(data):
        data['maxterm'] = False
        for i in range(2, len(data) - 2):
            if (data['Close'].iloc[i] > data['Close'].iloc[i - 1]) & (data['Close'].iloc[i] > data['Close'].iloc[i - 2]) & (data['Close'].iloc[i] > data['Close'].iloc[i + 1]) & (data['Close'].iloc[i] > data['Close'].iloc[i + 2]):
                data['maxterm'].iloc[i] = True
        return data

    def Fractal3(data):
        data['mintermr'] = False
        for i in range(2, len(data) - 2):
            if (data['Rsi'].iloc[i] < data['Rsi'].iloc[i - 1]) & (data['Rsi'].iloc[i] < data['Rsi'].iloc[i - 2]) & (data['Rsi'].iloc[i] < data['Rsi'].iloc[i + 1]) & (data['Rsi'].iloc[i] < data['Rsi'].iloc[i + 2]):
                data['mintermr'].iloc[i] = True
        return data

    def Fractal4(data):
        data['maxtermr'] = False
        for i in range(2, len(data) - 2):
            if (data['Rsi'].iloc[i] > data['Rsi'].iloc[i - 1]) & (data['Rsi'].iloc[i] > data['Rsi'].iloc[i - 2]) & (data['Rsi'].iloc[i] > data['Rsi'].iloc[i + 1]) & (data['Rsi'].iloc[i] > data['Rsi'].iloc[i + 2]):
                data['maxtermr'].iloc[i] = True
        return data

    def Divergence(data):
        data['DivergenceSignal'] = 0
        for i in range(2, len(data) - 1):
            if (data['Close'].iloc[i] < data['Close'].iloc[i - 1]) & (data['Rsi'].iloc[i] > data['Rsi'].iloc[i + 1]):
                data['DivergenceSignal'].iloc[i] = 1
            if (data['Close'].iloc[i] > data['Close'].iloc[i - 1]) & (data['Rsi'].iloc[i] < data['Rsi'].iloc[i + 1]):
                data['DivergenceSignal'].iloc[i] = -1
        return data

    def Signal(data):
        data['Signal'] = 0
        for i in range(len(data)):
            if (data['Rsi'].iloc[i] < 40) & (data['Close'].iloc[i] < (data['BBmid'].iloc[i]) / 2) & (data['VolumeDelta'].iloc[i] > 0) & (data['minterm'].iloc[i] == True) & (data['mintermr'].iloc[i]) == True:
                data['Signal'].iloc[i] = 1
            elif (data['Rsi'].iloc[i] > 60) & (data['Close'].iloc[i] > (data['BBmid'].iloc[i]) / 2) & (data['VolumeDelta'].iloc[i] < 0) & (data['maxterm'].iloc[i] == True) & (data['maxtermr'].iloc[i]) == True:
                data['Signal'].iloc[i] = -1
        return data

    def LogicPL(data, capital):
        positions = []
        quantity = 0
        final_capital=capital
        for i in range(len(data)-10):
            entry_price=data['Close'].iloc[i]
            quantity=math.floor(capital/data['Close'].iloc[i])
            exit_price=data['Close'].iloc[i+10]
            pl=(exit_price-entry_price)*quantity*data['Signal'].iloc[i]
            final_capital+=pl
            positions.append({ 'EntryPrice': entry_price,
                                       'ExitPrice': exit_price, 'PnL': pl, 'Quantity': quantity})
        print(data)
        print(positions)
        print(final_capital)


    def apply_conditions(ticker):
        a = Strategy.FetchData(ticker)
        b = Strategy.SetIndicator(a)
        c = Strategy.Fractal1(b)
        d = Strategy.Fractal2(c)
        e = Strategy.Fractal3(d)
        f = Strategy.Fractal4(e)  # final without divergence
        g = Strategy.Divergence(f)  
        h = Strategy.Signal(g)
        Strategy.LogicPL(h, capital)


    def s1():
        for stock in stocks:
            Strategy.apply_conditions(stock)

Strategy.s1()