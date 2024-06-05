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

capital = 10000
startdate = datetime.datetime(2023, 8, 1)
enddate = datetime.datetime(2024, 1, 1)
stocks = ['BTCUSDT']

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
            df[['open', 'high', 'low', 'Close', 'Volume', 'VolumeUSD']] = df[['open', 'high', 'low', 'Close', 'Volume', 'VolumeUSD']].apply(pd.to_numeric)
            print(df.head())
            return df
        else:
            print("Error: Unexpected response format")
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'Close', 'Volume', 'VolumeUSD'])

    def place_order(self, category="spot", symbol="BTCUSDT", side="Buy", orderType="Market", qty="0.1"):
        clientOrderId = str(uuid.uuid4())
        return self.session.place_order(
            category=category,
            symbol=symbol,
            side=side,
            orderType=orderType,
            qty=qty,
            clientOrderId=clientOrderId,
        )    

class Strategy(TradingSession):
    def __init__(self, ticker, startdate, enddate, capital):
        super().__init__()  # Initialize the TradingSession
        self.ticker = ticker
        self.startdate = startdate
        self.enddate = enddate
        self.capital = capital
        self.data = None

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
                    self.data.loc[i, 'minterm'] = True
        return self.data

    def Fractal2(self):
        self.data['mintermr'] = False
        n=2
        for i in range(2, len(self.data) - 2):
            for j in range(n):
                if (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i - j]) & (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i + j]):
                    self.data.loc[i, 'mintermr'] = True
        return self.data

    def Fractal3(self):
        self.data['maxterm'] = False
        n=2
        for i in range(2, len(self.data) - 2):
            for j in range(n):
                if (self.data['Close'].iloc[i] > self.data['Close'].iloc[i - j]) & (self.data['Close'].iloc[i] > self.data['Close'].iloc[i + j]):
                    self.data.loc[i, 'maxterm'] = True
        return self.data

    def Fractal4(self):
        self.data['maxtermr'] = False
        n=2
        for i in range(2, len(self.data) - 2):
            for j in range(n):
                if (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i - j]) & (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i + j]):
                    self.data.loc[i, 'maxtermr'] = True
        return self.data

    def Divergence(self, data):
        data['DivergenceSignal'] = 0
        n=3
        for i in range(2, len(data) - n):
            for j in range(1, n+1):
                if (data['Close'].iloc[i] < data['Close'].iloc[i - j]) & (data['Rsi'].iloc[i] > data['Rsi'].iloc[i + j]):
                    data.loc[i, 'DivergenceSignal'] = 1
                elif (data['Close'].iloc[i] > data['Close'].iloc[i - j]) & (data['Rsi'].iloc[i] < data['Rsi'].iloc[i + j]):
                    data.loc[i, 'DivergenceSignal'] = -1
        return data
    
    def Signal1(self, data):
        data['Signal1'] = 0
        for i in range(len(data)):
            if (data['DivergenceSignal'].iloc[i] == 1) and (data['Rsi'].iloc[i] < 50) and (data['BBmid'].iloc[i] > data['Close'].iloc[i]):
                data.loc[i, 'Signal1'] = 1
        return data
    
    def Signal2(self, data):
        data['Signal2'] = 0
        for i in range(len(data)):
            if (data['DivergenceSignal'].iloc[i] == -1) and (data['Rsi'].iloc[i] > 50) and (data['BBmid'].iloc[i] < data['Close'].iloc[i]):
                data.loc[i, 'Signal2'] = -1
        return data
    
    def execute_trades1(self, data):
        sessionfinal = TradingSession()
        latest_signal = data['Signal1'].iloc[-1]
        if latest_signal == 1:
            print(f"Buy signal detected for {self.ticker}. Placing order.")
            sessionfinal.place_order(category="spot", symbol=self.ticker, side="Buy", orderType="Market", qty=0.01)
        elif latest_signal == 0:
            print("The Signal is 0, no order will be placed.")

    def execute_trades2(self, data):
        sessionfinal = TradingSession()
        latest_signal = data['Signal2'].iloc[-1]
        if latest_signal == -1:
            print(f"Sell signal detected for {self.ticker}. Placing order.")
            sessionfinal.place_order(category="spot", symbol=self.ticker, side="Sell", orderType="Market", qty=0.01)
        elif latest_signal == 0:
            print("The Signal is 0, no order will be placed.")
    
    def apply_conditions(self):
        while True:
            self.data = self.get_kline()  # Fixed: self.data should be assigned here
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

            ex1 = self.execute_trades1(Sgn1)
            ex2 = self.execute_trades2(Sgn2)

            Sgn1.to_csv(f"file1_{self.ticker}.csv")
            Sgn2.to_csv(f"file2_{self.ticker}.csv")
            print(ex1)
            print(ex2)
            time.sleep(60)

def main():
    for ticker in stocks:
        strategy = Strategy(ticker, startdate, enddate, capital)
        strategy.apply_conditions()

if __name__ == '__main__':
    main()
