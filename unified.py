import yfinance as yf
import talib
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
import time
from wrapper import TradingSession
import creds

# Convert startdate and enddate to timestamps
startdate = int(datetime.datetime(2020, 1, 1).timestamp())
enddate = int(datetime.datetime(2022, 1, 1).timestamp())

class Strategy:
    def __init__(self, ticker,capital):
        self.ticker = ticker
        self.capital = capital
        self.data = None

    def FetchData(self):
        Session = TradingSession(testnet=True,api_key=creds.apikey,api_secret=creds.apisecret)
        self.data = Session.get_kline(category="spot",symbol=self.ticker,interval=60,start=startdate,end=enddate)
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
    
    def execute_trades(self):
        sessioninitial=TradingSession()
        for i in range(len(self.data)):
            if self.data['Signal'] == 1:
                print(f"Buy signal detected for {self.ticker}. Placing order.")
                sessioninitial.place_order()
            elif self.data['Signal'] == -1:
                print(f"Sell signal detected for {self.ticker}. Placing order.")
                sessioninitial.cancel_all_orders()

    def run_live_analysis(self):
        while True:
            raw_data = self.FetchData()
            data_indicator = self.SetIndicator(raw_data)
            data_indicator2=self.Fractal1(data_indicator)
            data_indicator3=self.Fractal2(data_indicator2)
            data_indicator4=self.Fractal3(data_indicator3)
            data_indicator5=self.Fractal4(data_indicator4)
            data_indicator6=self.Divergence(data_indicator5)
            data_signal = self.Signal(data_indicator6)
            self.execute_trades(data_signal)
            time.sleep(60)  # Wait for 1 minute before fetching new data

if __name__ == "__main__":
    api_key=creds.apikey
    api_secret_key=creds.apisecret
    bybit_client = TradingSession(api_key, api_secret_key)

    stocks = ['BTCUSDT','ETHUSDT','ETCUSDT','LTCUSDT','XRPUSDT','EOSUSDT']  # Add more symbols if needed
    for stock_symbol in stocks:
        stock_analysis = Strategy(stock_symbol, bybit_client)
        stock_analysis.run_live_analysis()


"""    def LogicPL(self):
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
        summarysheet.to_csv(os.path.join('Data', f'summary_{self.ticker}.csv'))"""

"""    def graph(self):
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

        this code to be placed in the strategy class
        
        """

"""    def apply_conditions(self):
        self.FetchData()
        self.SetIndicator()
        self.Fractal1()
        self.Fractal2()
        self.Fractal3()
        self.Fractal4()  
        self.Divergence()
        self.Signal()
        self.LogicPL()
        self.graph()"""