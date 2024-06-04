#working
import yfinance as yf
import talib
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import math

capital = 10000
startdate = datetime.datetime(2017, 8, 1)
enddate = datetime.datetime(2024, 1, 1)
stocks = ['MSFT','AAPL']

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
        return self.data

    def Fractal1(self):
        self.data['minterm'] = False
        n=2
        for i in range(2, len(self.data) - 2):
            for j in range(n):
                if (self.data['Close'].iloc[i] < self.data['Close'].iloc[i - j]) & (self.data['Close'].iloc[i] < self.data['Close'].iloc[i + j]):
                    self.data['minterm'].iloc[i] = True
        return self.data

    def Fractal2(self):
        self.data['mintermr'] = False
        n=2
        for i in range(2, len(self.data) - 2):
            for j in range(n):
                if (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i - j]) & (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i + j]):
                    self.data['mintermr'].iloc[i] = True
        return self.data

    def Fractal3(self):
        self.data['maxterm'] = False
        n=2
        for i in range(2, len(self.data) - 2):
            for j in range(n):
                if (self.data['Close'].iloc[i] > self.data['Close'].iloc[i - j]) & (self.data['Close'].iloc[i] > self.data['Close'].iloc[i + j]):
                    self.data['maxterm'].iloc[i] = True
        return self.data

    def Fractal4(self):
        self.data['maxtermr'] = False
        n=2
        for i in range(2, len(self.data) - 2):
            for j in range(n):
                if (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i - j]) & (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i + j]):
                    self.data['maxtermr'].iloc[i] = True
        return self.data

    def Divergence(self,data):
        data['DivergenceSignal'] = 0
        n=3
        for i in range(2, len(data) - n):
            for j in range(1,n+1):
                if (data['Close'].iloc[i] < self.data['Close'].iloc[i - j]) & (data['Rsi'].iloc[i] > data['Rsi'].iloc[i + j]):
                    data['DivergenceSignal'].iloc[i] = 1
                elif (data['Close'].iloc[i] > data['Close'].iloc[i - j]) & (data['Rsi'].iloc[i] < data['Rsi'].iloc[i + j]):
                    data['DivergenceSignal'].iloc[i] = -1
        return data
    
    def Signal1(self,data):
        data['Signal1']=0
        for i in range(len(data)):
            if (data['DivergenceSignal'].iloc[i])==1 and (data['Rsi'].iloc[i]<50) and (data['BBmid'].iloc[i]>data['Close'].iloc[i]):
                data['Signal1'].iloc[i]=1
        return data
    
    def Signal2(self,data):
        data['Signal2']=0
        for i in range(len(data)):
            if (data['DivergenceSignal'].iloc[i])==-1 and (data['Rsi'].iloc[i]>50) and (data['BBmid'].iloc[i]<data['Close'].iloc[i]):
                data['Signal2'].iloc[i] = -1
        return data

    def apply_conditions(self):
        self.FetchData()
        self.SetIndicator()
        self.Fractal1()
        self.Fractal2()
        self.Fractal3()
        self.Fractal4()  
        fractal_df1 = self.data[(self.data['minterm'] == True) & (self.data['mintermr'] == True)]
        fractal_df2 = self.data[(self.data['maxterm'] == True) & (self.data['maxtermr'] == True)]
        
        # Apply Divergence on fractal_df1 and fractal_df2 separately
        divergence_df1 = self.Divergence(fractal_df1)
        divergence_df2 = self.Divergence(fractal_df2)
        
        Sgn1 = self.Signal1(divergence_df1)
        Sgn2 = self.Signal2(divergence_df2)
        
        Sgn1.to_csv(f"file1_{self.ticker}.csv")
        Sgn2.to_csv(f"file2_{self.ticker}.csv")
        print(Sgn1)
        print(Sgn2)


def main():
    for ticker in stocks:
        strategy = Strategy(ticker, startdate, enddate, capital)
        strategy.apply_conditions()

if __name__ == '__main__':
    main()
