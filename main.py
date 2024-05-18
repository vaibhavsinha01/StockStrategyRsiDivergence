import yfinance as yf
import talib
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
from creds import userID, passwordID

capital = 10000
startdate = datetime.datetime(2021, 1, 1)
enddate = datetime.datetime(2024, 1, 1)
stocks = ['MSFT', 'AAPL', 'GOOGL', 'TSLA']

class Broker:
    def __init__(self, balance):
        self.balance = balance
        self.stocks = {}

    def login(self, username, password):
        if username == userID and password == passwordID:
            print("You have successfully logged in")
            return True
        else:
            print("Your password or username is wrong")
            return False

    def buy_stock(self, symbol, quantity, price):
        cost = quantity * price
        if cost > self.balance:
            print("Insufficient balance")
            return False
        else:
            if symbol in self.stocks:
                self.stocks[symbol] += quantity
            else:
                self.stocks[symbol] = quantity
            self.balance -= cost
            print(f"Bought {quantity} shares of {symbol} at ${price} each. Remaining balance: ${self.balance}")
            return True
        
    def sell_stock(self, symbol, quantity, price):
        if symbol not in self.stocks or self.stocks[symbol] < quantity:
            print(f"Not enough {symbol} shares to sell.")
            return False
        else:
            self.stocks[symbol] -= quantity
            self.balance += quantity * price
            print(f"Sold {quantity} shares of {symbol} at ${price} each. Remaining balance: ${self.balance}")
            return True
        
    def get_balance(self):
        return self.balance

    def get_portfolio(self):
        return self.stocks

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

    def LogicPL(self):
        positions = []
        final_capital = self.capital
        for i in range(len(self.data) - 10):
            entry_price = self.data['Close'].iloc[i]
            quantity = math.floor(self.capital / entry_price)
            exit_price = self.data['Close'].iloc[i + 10]
            pl = (exit_price - entry_price) * quantity * self.data['Signal'].iloc[i]
            final_capital += pl
            positions.append({
                'EntryPrice': entry_price,
                'ExitPrice': exit_price,
                'PnL': pl,
                'Quantity': quantity
            })
        print(self.data)
        print(positions)
        print(final_capital)
        summarysheet = pd.DataFrame(positions)
        summarysheet.to_csv(os.path.join('Data', f'summary_{self.ticker}.csv'))

    def graph(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8))
        ax1.plot(self.data['Close'], label='Close Price', color='black')
        ax1.set_title(f"Close price of {self.ticker}", color='black')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Close Price')
        ax1.grid(True)
        ax2.plot(self.data['Rsi'], label='RSI', color='black')
        ax2.set_title(f"RSI of {self.ticker}", color='black')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('RSI')
        ax2.grid(True)
        plt.savefig(os.path.join('Data', f'{self.ticker}_stock_price_graph.png'), format='png')
        plt.close()

    def apply_conditions(self):
        self.FetchData()
        self.SetIndicator()
        self.Fractal1()
        self.Fractal2()
        self.Fractal3()
        self.Fractal4()  
        self.Divergence()
        self.Signal()
        self.LogicPL()
        self.graph()

def main():
    broker = Broker(capital)
    if not broker.login(userID, passwordID):
        return

    for ticker in stocks:
        strategy = Strategy(ticker, startdate, enddate, capital)
        strategy.apply_conditions()

if __name__ == '__main__':
    main()
