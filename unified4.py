import datetime
import time
import talib
import pandas as pd
from wrapper import TradingSession  # Assuming 'wrapper' contains the TradingSession class
import creds
from pybit.exceptions import InvalidRequestError  # Import the InvalidRequestError

# Convert startdate and enddate to timestamps
startdate = int(datetime.datetime(2020, 1, 1).timestamp())
enddate = int(datetime.datetime(2022, 1, 1).timestamp())

class Strategy:
    def __init__(self, ticker, client):
        self.ticker = ticker
        self.bybit_client = client
        self.data = None

    def fetch_data(self):
        historical_data = self.bybit_client.get_kline(symbol=self.ticker, start=startdate, end=enddate)
        data = pd.DataFrame(historical_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        data["open"] = data["open"].astype(float)
        data["high"] = data["high"].astype(float)
        data["close"] = data["close"].astype(float)
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)
        self.data = data
        return data

    def set_indicator(self):
        if 'close' not in self.data.columns:
            raise KeyError("The fetched data does not contain 'close' column. Please check the data structure.")
        self.data['rsi'] = talib.RSI(self.data['close'], timeperiod=14)
        self.data['bb_upper'], self.data['bb_middle'], self.data['bb_lower'] = talib.BBANDS(self.data['close'], timeperiod=14)
        self.data['volume_delta'] = self.data['volume'].diff()
        self.find_fractal(self.data, kind='min')
        self.find_fractal(self.data, kind='max')
        return self.data
    
    def find_fractal(self, data, kind='min'):
        data[f'{kind}_fractal'] = False
        for i in range(2, len(data) - 2):
            if (data['close'].iloc[i] < data['close'].iloc[i - 1]) & (data['close'].iloc[i] < data['close'].iloc[i - 2]) & (data['close'].iloc[i] < data['close'].iloc[i + 1]) & (data['close'].iloc[i] < data['close'].iloc[i + 2]):
                data[f'{kind}_fractal'].iloc[i] = True
        return data

    def divergence(self):
        self.data['divergence_signal'] = 0
        for i in range(2, len(self.data) - 1):
            if (self.data['close'].iloc[i] < self.data['close'].iloc[i - 1]) & (self.data['rsi'].iloc[i] > self.data['rsi'].iloc[i + 1]):
                self.data['divergence_signal'].iloc[i] = 1
            if (self.data['close'].iloc[i] > self.data['close'].iloc[i - 1]) & (self.data['rsi'].iloc[i] < self.data['rsi'].iloc[i + 1]):
                self.data['divergence_signal'].iloc[i] = -1
        return self.data
    
    def signal(self):
        self.data['signal'] = 0
        for i in range(len(self.data)):
            if (self.data['rsi'].iloc[i] < 40) & (self.data['close'].iloc[i] < (self.data['bb_middle'].iloc[i]) / 2) & (self.data['volume_delta'].iloc[i] > 0) & (self.data['min_fractal'].iloc[i]) & (self.data['min_fractal_rsi'].iloc[i]):
                self.data['signal'].iloc[i] = 1
            elif (self.data['rsi'].iloc[i] > 60) & (self.data['close'].iloc[i] > (self.data['bb_middle'].iloc[i]) / 2) & (self.data['volume_delta'].iloc[i] < 0) & (self.data['max_fractal'].iloc[i]) & (self.data['max_fractal_rsi'].iloc[i]):
                self.data['signal'].iloc[i] = -1
        return self.data
    
    def execute_trades(self):
        session = TradingSession(api_key, api_secret_key)
        for i in range(len(self.data)):
            try:
                if self.data['signal'].iloc[i] == 1:
                    print(f"Buy signal detected for {self.ticker}. Placing order.")
                    session.place_order(symbol=self.ticker, qty=0.01, side='Buy', orderType='Limit', price=1, timeInForce='PostOnly', clientOrderId='2599af16-1c40-4e00-91ed-ac71bd61e883')
                elif self.data['signal'].iloc[i] == -1:
                    print(f"Sell signal detected for {self.ticker}. Placing order.")
                    session.place_order(symbol=self.ticker, qty=0.01, side='Sell', orderType='Limit', price=1, timeInForce='PostOnly', clientOrderId='2599af16-1c40-4e00-91ed-ac71bd61e883')
            except InvalidRequestError as e:
                print(f"Error placing order: {e}")
                # Handle insufficient balance error here
                # You can log the error and take appropriate actions

    def run_live_analysis(self):
        while True:
            self.fetch_data()
            self.set_indicator()
            self.divergence()
            self.signal()
            self.execute_trades()
            time.sleep(60)  # Wait for 1 minute before fetching new data

if __name__ == "__main__":
    api_key = creds.apikey
    api_secret_key = creds.apisecret

    stocks = ['BTCUSDT', 'ETHUSDT', 'ETCUSDT', 'LTCUSDT', 'XRPUSDT', 'EOSUSDT']  # Add more symbols if needed
    for stock_symbol in stocks:
        bybit_client = TradingSession(api_key, api_secret_key)
        stock_analysis = Strategy(stock_symbol, bybit_client)
        stock_analysis.run_live_analysis()
