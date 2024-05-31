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
        
    def get_kline(self, category="spot", symbol="BTCUSDT", interval=60, start=1670601600000, end=1670608800000):
        return self.session.get_kline(
            category=category,
            symbol=symbol,
            interval=interval,
            start=start,
            end=end,
        )
        
    def orderbook(self, category='spot', symbol='BTCUSDT'):
        return self.session.get_orderbook(
            category=category,
            symbol=symbol,
        )
        
    def place_order(self, category="spot", symbol="BTCUSDT", side="Buy", orderType="Limit", qty="0.01", price="100", timeInForce="PostOnly"):
        clientOrderId = str(uuid.uuid4())
        return self.session.place_order(
            category=category,
            symbol=symbol,
            side=side,
            orderType=orderType,
            qty=qty,
            price=price,
            timeInForce=timeInForce,
            clientOrderId=clientOrderId,
        )

        
    def cancel_all_orders(self, category="linear", settleCoin="USDT"):
        return self.session.cancel_all_orders(
            category=category,
            settleCoin=settleCoin,
        )
        
    def get_recent_trades(self, category='spot', symbol='BTCUSDT', limit=1):
        return self.session.get_public_trade_history(
            category=category,
            symbol=symbol,
            limit=limit
        )
        
    def account_balance(self, accountType='UNIFIED', coin='BTC'):
        return self.session.get_wallet_balance(
            accountType=accountType,
            coin=coin
        )
        
    def cancel_order(self, category='spot', symbol='BTCUSDT', orderId="c6f055d9-7f21-4079-913d-e6523a9cfffa"):
        return self.session.cancel_order(
            category=category,
            symbol=symbol,
            orderId=orderId
        )
        
    def fee_rate_info(self, symbol='BTCUSDT'):
        return self.session.get_fee_rates(symbol=symbol)
    
    def coin_balance(self, accountType='UNIFIED', coin='USDC'):
        return self.session.get_coins_balance(accountType=accountType, coin=coin)
    
    def get_positions(self, category='linear', symbol='BTCUSDT'):
        return self.session.get_positions(category=category, symbol=symbol)
    
    def historical_volatility(self, category='spot', baseCoin='BTC', period=30):
        return self.session.get_historical_volatility(category=category, baseCoin=baseCoin, period=period)

    def tickers(self, category='spot', symbol='BTCUSDT'):
        return self.session.get_tickers(category=category, symbol=symbol)



class Strategy(TradingSession):
    def __init__(self, ticker, startdate, enddate, capital, session=None):
        super().__init__()  # Initialize the parent class
        self.ticker = ticker
        self.startdate = startdate
        self.enddate = enddate
        self.capital = capital
        self.data = None
        self.session = session

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

    def execute_trades(self):
        sessioninitial = TradingSession()
        for i in range(len(self.data)):
            if self.data['Signal'].iloc[i] == 1:
                print(f"Buy signal detected for {self.ticker}. Placing order.")
                sessioninitial.place_order(category="spot", symbol=self.ticker, side="Buy", orderType="Limit", qty=0.01, price=100, timeInForce="PostOnly")
            elif self.data['Signal'].iloc[i] == -1:
                print(f"Sell signal detected for {self.ticker}. Placing order.")
                sessioninitial.place_order(category="spot", symbol=self.ticker, side="Sell", orderType="Limit", qty=0.01, price=100, timeInForce="PostOnly")


    def apply_conditions(self):
        self.get_kline()
        self.SetIndicator()
        self.Fractal1()
        self.Fractal2()
        self.Fractal3()
        self.Fractal4()  
        self.Divergence()
        self.Signal()
        self.execute_trades()

def main():
    trading_session = TradingSession()
    stocks = ['BTCUSDT', 'ETHUSDT']
    for stock in stocks:
        session = Strategy(stock, startdate=startdate, enddate=enddate, capital=capital, session=trading_session)
        session.apply_conditions()

if __name__ == '__main__':
    main()

