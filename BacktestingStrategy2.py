from backtesting import Backtest, Strategy
import talib
import yfinance as yf
import datetime
import pandas as pd

# Global parameters
startdate = datetime.datetime(2020, 1, 1)
enddate = datetime.datetime(2024, 1, 1)
capital = 10000
stocks = ['MSFT', 'AAPL', 'GOOGL', 'TSLA', 'JPM']

def optimfunc(series):
    if series["# Trades"] < 10:
        return -1
    else:
        return series['Equity Final [$]']

class MyStrategy(Strategy):
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
            return

        rsi = self.daily_rsi[-1]
        price = self.data.Close[-1]
        bollinger_mid = self.bollinger_middle[-1]

        prev_rsi = self.daily_rsi[-2]
        prev_price = self.data.Close[-2]

        # Bullish divergence
        if rsi < self.lower_bound_rsi and price < bollinger_mid and rsi > prev_rsi and price < prev_price:
            self.position.close()
            self.buy(sl=(self.stlo * price) / 100, tp=(self.tkpr * price) / 100)
        
        # Bearish divergence
        elif rsi > self.upper_bound_rsi and price > bollinger_mid and rsi < prev_rsi and price > prev_price:
            self.position.close()
            self.sell(tp=(self.stlo * price) / 100, sl=(self.tkpr * price) / 100)

def fetch_data(ticker, startdate, enddate):
    data = yf.download(ticker, start=startdate, end=enddate, interval='1d')
    data.drop('Adj Close', axis=1, inplace=True)
    return data

class ExtendedStrategy:
    def __init__(self, ticker, startdate, enddate, capital):
        self.ticker = ticker
        self.startdate = startdate
        self.enddate = enddate
        self.capital = capital
        self.data = None

    def apply_conditions(self):
        self.data = fetch_data(self.ticker, self.startdate, self.enddate)
        self.set_indicators()
        self.calculate_fractals()
        self.detect_divergence()
        self.generate_signals()
        return self.data

    def set_indicators(self):
        self.data['Rsi'] = talib.RSI(self.data['Close'], timeperiod=14)
        self.data['BBup'], self.data['BBmid'], self.data['BBlow'] = talib.BBANDS(self.data['Close'], timeperiod=14)
        self.data['VolumeDelta'] = self.data['Volume'].diff()

    def calculate_fractals(self):
        for i in range(len(self.data)):
            self.data['minterm'] = ((self.data['Close'].iloc[i] < self.data['Close'].iloc[i+1]) &(self.data['Close'].iloc[i] < self.data['Close'].iloc[i+2]) &(self.data['Close'].iloc[i] < self.data['Close'].iloc[i-1]) &(self.data['Close'].iloc[i] < self.data['Close'].iloc[i-2]))
            self.data['maxterm'] = ((self.data['Close'].iloc[i] > self.data['Close'].iloc[i-1]) &(self.data['Close'].iloc[i] > self.data['Close'].iloc[i-2]) &(self.data['Close'].iloc[i] > self.data['Close'].iloc[i-1]) &(self.data['Close'].iloc[i] > self.data['Close'].iloc[i-2]))
            self.data['mintermr'] = ((self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i]) &(self.data['Rsi'].iloc[i+2] < self.data['Rsi'].iloc[i+1]) &(self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i-1]) &(self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i-2]))
            self.data['maxtermr'] = ((self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i]) &(self.data['Rsi'].iloc[i+2] > self.data['Rsi'].iloc[i+1]) &(self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i-1]) &(self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i-2]))

    def detect_divergence(self):
        self.data['DivergenceSignal'] = 0
        for i in range(2, len(self.data) - 1):
            if (self.data['Close'].iloc[i] < self.data['Close'].iloc[i - 1]) and (self.data['Rsi'].iloc[i] > self.data['Rsi'].iloc[i + 1]):
                self.data['DivergenceSignal'].iloc[i] = 1
            if (self.data['Close'].iloc[i] > self.data['Close'].iloc[i - 1]) and (self.data['Rsi'].iloc[i] < self.data['Rsi'].iloc[i + 1]):
                self.data['DivergenceSignal'].iloc[i] = -1

    def generate_signals(self):
        self.data['Signal'] = 0
        for i in range(len(self.data)):
            if (self.data['Rsi'].iloc[i] < 40) and (self.data['Close'].iloc[i] < (self.data['BBmid'].iloc[i]) / 2) and (self.data['VolumeDelta'].iloc[i] > 0) and self.data['minterm'].iloc[i] and self.data['mintermr'].iloc[i]:
                self.data['Signal'].iloc[i] = 1
            elif (self.data['Rsi'].iloc[i] > 60) and (self.data['Close'].iloc[i] > (self.data['BBmid'].iloc[i]) / 2) and (self.data['VolumeDelta'].iloc[i] < 0) and self.data['maxterm'].iloc[i] and self.data['maxtermr'].iloc[i]:
                self.data['Signal'].iloc[i] = -1

def main():
    for ticker in stocks:
        strategy = ExtendedStrategy(ticker, startdate, enddate, capital)
        data = strategy.apply_conditions()

        # Backtest with MyStrategy
        bt = Backtest(data, MyStrategy, cash=capital)
        stats = bt.run()
        print(f"Backtest results for {ticker}:")
        print(stats)
        bt.plot()

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
