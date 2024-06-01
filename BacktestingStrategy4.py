from backtesting import Backtest, Strategy
import talib
import yfinance as yf
import datetime
import pandas as pd

# Global parameters
startdate = datetime.datetime(2020, 1, 1)
enddate = datetime.datetime(2024, 1, 1)
capital = 10000
stocks = ['MSFT']

def optimfunc(series):
    if series["# Trades"] < 10:
        return -1
    else:
        return series['Equity Final [$]']

def fetch_data(ticker, startdate, enddate):
    data = yf.download(ticker, start=startdate, end=enddate, interval='1d')
    data.drop('Adj Close', axis=1, inplace=True)
    return data

def set_indicators(data):
    data['Rsi'] = talib.RSI(data['Close'], timeperiod=14)
    data['BBup'], data['BBmid'], data['BBlow'] = talib.BBANDS(data['Close'], timeperiod=14)
    data['VolumeDelta'] = data['Volume'].diff()
    return data

def calculate_fractals(data):
    data['minterm'] = (data['Close'].shift(2) > data['Close'].shift(1)) & (data['Close'].shift(1) > data['Close']) & (data['Close'] < data['Close'].shift(-1)) & (data['Close'] < data['Close'].shift(-2))
    data['maxterm'] = (data['Close'].shift(2) < data['Close'].shift(1)) & (data['Close'].shift(1) < data['Close']) & (data['Close'] > data['Close'].shift(-1)) & (data['Close'] > data['Close'].shift(-2))
    data['mintermr'] = (data['Rsi'].shift(2) > data['Rsi'].shift(1)) & (data['Rsi'].shift(1) > data['Rsi']) & (data['Rsi'] < data['Rsi'].shift(-1)) & (data['Rsi'] < data['Rsi'].shift(-2))
    data['maxtermr'] = (data['Rsi'].shift(2) < data['Rsi'].shift(1)) & (data['Rsi'].shift(1) < data['Rsi']) & (data['Rsi'] > data['Rsi'].shift(-1)) & (data['Rsi'] > data['Rsi'].shift(-2))
    return data

def detect_divergence(data):
    data['DivergenceSignal'] = 0
    for i in range(2, len(data) - 1):
        if (data['Close'].iloc[i] < data['Close'].iloc[i - 1]) and (data['Rsi'].iloc[i] > data['Rsi'].iloc[i + 1]):
            data['DivergenceSignal'].iloc[i] = 1
        if (data['Close'].iloc[i] > data['Close'].iloc[i - 1]) and (data['Rsi'].iloc[i] < data['Rsi'].iloc[i + 1]):
            data['DivergenceSignal'].iloc[i] = -1
    return data

def generate_signals(data):
    data['Signal'] = 0
    for i in range(len(data)):
        if (data['Rsi'].iloc[i] < 40) and (data['Close'].iloc[i] < (data['BBmid'].iloc[i]) / 2) and (data['VolumeDelta'].iloc[i] > 0) and data['minterm'].iloc[i] and data['mintermr'].iloc[i]:
            data['Signal'].iloc[i] = 1
        elif (data['Rsi'].iloc[i] > 60) and (data['Close'].iloc[i] > (data['BBmid'].iloc[i]) / 2) and (data['VolumeDelta'].iloc[i] < 0) and data['maxterm'].iloc[i] and data['maxtermr'].iloc[i]:
            data['Signal'].iloc[i] = -1
    return data


class MyStrategy(Strategy):
    upper_bound_rsi = 70
    lower_bound_rsi = 30
    rsi_window = 14
    bb_window = 14
    stlo = 97
    tkpr = 110

    def init(self):
        ticker = self.data.index.name
        fetched_data = fetch_data(ticker, startdate, enddate)
        data_with_indicators = set_indicators(fetched_data)
        data_with_fractals = calculate_fractals(data_with_indicators)
        data_with_divergence = detect_divergence(data_with_fractals)
        data_with_signals = generate_signals(data_with_divergence)
        return data_with_signals


    def next(self):
        if len(self.data['Close']) < 15:  # Ensure we have enough data points
            return -1
        
        price=self.data['Close']

        # Bullish divergence
        if self.data['Signal']==1:
            self.position.close()
            self.buy(sl=(self.stlo * price) / 100, tp=(self.tkpr * price) / 100)
        
        # Bearish divergence
        elif self.data['Signal']==-1:
            self.position.close()
            self.sell(tp=(self.stlo * price) / 100, sl=(self.tkpr * price) / 100)

def main():
    for ticker in stocks:
        # Fetch data
        fetched_data = fetch_data(ticker, startdate, enddate)
        data_with_indicators = set_indicators(fetched_data)
        data_with_fractals = calculate_fractals(data_with_indicators)
        data_with_divergence = detect_divergence(data_with_fractals)
        data_with_signals = generate_signals(data_with_divergence)
        

        # Backtest with MyStrategy
        bt = Backtest(data_with_signals, MyStrategy, cash=capital)
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
