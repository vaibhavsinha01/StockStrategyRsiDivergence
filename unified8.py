import yfinance as yf
import talib
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
from pybit.unified_trading import HTTP
import creds
import uuid
import time

# This code uses RSI along with Bollinger Bands and fractal points to take trades.

capital = 10000
startdate = datetime.datetime(2021, 1, 1)
enddate = datetime.datetime(2024, 1, 1)

class TradingSession:
    def __init__(self, testnet=True, api_key=creds.apikey, api_secret=creds.apisecret):
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret,
        )
        
    def get_kline(self, category="spot", symbol="BTCUSDT", interval=60):
        response = self.session.get_kline(
            category=category,
            symbol=symbol,
            interval=interval,
        )
        print(response)  # Print the entire response to debug
        if 'result' in response and 'list' in response['result']:
            data = response['result']['list']
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'Close', 'Volume', 'VolumeUSD'])
            print(df.head())
            return df
        else:
            print("Error: Unexpected response format")
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'Close', 'Volume', 'VolumeUSD'])

    def place_order(self, category="spot", symbol="BTCUSDT", side="Buy", orderType="Market", qty="0.01", timeInForce="PostOnly"):
        clientOrderId = str(uuid.uuid4())
        return self.session.place_order(
            category=category,
            symbol=symbol,
            side=side,
            orderType=orderType,
            qty=qty,
            timeInForce=timeInForce,
            clientOrderId=clientOrderId,
        )    

class Strategy(TradingSession):
    def __init__(self, ticker, startdate, enddate, capital, session=None):
        super().__init__()  
        self.ticker = ticker
        self.data = None
        self.startdate = startdate
        self.enddate = enddate
        self.capital = capital
        self.session = session

    def SetIndicator(self):
        self.data['Rsi'] = talib.RSI(self.data['Close'], timeperiod=14)
        self.data['BBup'], self.data['BBmid'], self.data['BBlow'] = talib.BBANDS(self.data['Close'], timeperiod=14)
        return self.data

    def Fractal1(self):
        self.data['minterm'] = False
        n=2
        for i in range(2, len(self.data) - 2):
            for j in range(n):
                if (self.data['Close'].iloc[i] > self.data['Close'].iloc[i - j]) & (self.data['Close'].iloc[i] > self.data['Close'].iloc[i + j]):
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
            if (self.data['Rsi'].iloc[i] < 40) & (self.data['Close'].iloc[i] < (self.data['BBmid'].iloc[i]) / 2) & (self.data['minterm'].iloc[i] == True) & (self.data['mintermr'].iloc[i] == True):
                self.data['Signal'].iloc[i] = 1
            elif (self.data['Rsi'].iloc[i] > 60) & (self.data['Close'].iloc[i] > (self.data['BBmid'].iloc[i]) / 2)  & (self.data['maxterm'].iloc[i] == True) & (self.data['maxtermr'].iloc[i] == True):
                self.data['Signal'].iloc[i] = -1
        return self.data
    
    def execute_trades(self):
        sessionfinal = TradingSession()
        latest_signal = self.data['Signal'].iloc[-1]
        if latest_signal == 1:
            print(f"Buy signal detected for {self.ticker}. Placing order.")
            sessionfinal.place_order(category="spot", symbol=self.ticker, side="Buy", orderType="Market", qty=0.01)
        elif latest_signal == -1:
            print(f"Sell signal detected for {self.ticker}. Placing order.")
            sessionfinal.place_order(category="spot", symbol=self.ticker, side="Sell", orderType="Market", qty=0.01)
        elif latest_signal == 0:
            print("The Signal is 0, no order will be placed.")
    
    def apply_conditions(self):
        while True:
            df = self.get_kline()
            if df is not None and not df.empty:
                self.data = df
                self.data['open'] = self.data['open'].astype(float)
                self.data['Close'] = self.data['Close'].astype(float)
                self.data['high'] = self.data['high'].astype(float)
                self.data['low'] = self.data['low'].astype(float)
                self.SetIndicator()
                self.Fractal1()
                self.Fractal2()
                self.Fractal3()
                self.Fractal4()
                
                # Create a column where both minterm and mintermr are True
                self.data['BothTrue'] = self.data['minterm'] & self.data['mintermr']
                true_elements_df = self.data[self.data['BothTrue']]
                
                self.Divergence()
                self.Signal()
                self.execute_trades()
            else:
                print("No valid data received. Skipping this iteration.")
            time.sleep(60)

def main():
    trading_session = TradingSession()
    stocks = ['BTCUSDT']
    for stock in stocks:
        session = Strategy(stock, startdate=startdate, enddate=enddate, capital=capital, session=trading_session)
        session.apply_conditions()

if __name__ == '__main__':
    main()
