import pandas as pd
import talib
from wrapper import TradingSession  # Assuming this is the correct import for TradingSession
import creds  # Assuming this contains apikey and apisecret

class Strategy:
    def __init__(self, ticker, capital):
        self.ticker = ticker
        self.capital = capital
        self.data = None

    def FetchData(self):
        startdate = '1670601600000'  # Example start date in milliseconds
        enddate = '1670608800000'    # Example end date in milliseconds

        Session = TradingSession(testnet=True, api_key=creds.apikey, api_secret=creds.apisecret)
        response = Session.get_kline(category="spot", symbol=self.ticker, interval=60, start=startdate, end=enddate)
        print("Raw response:", response)  # Print the raw response to see its structure

        if 'result' in response and 'list' in response['result']:
            kline_data = response['result']['list']
            if kline_data:
                columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Other']
                self.data = pd.DataFrame(kline_data, columns=columns)

                # Convert timestamp to datetime
                self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], unit='ms')
                
                # Convert relevant columns to numeric types
                self.data[['Open', 'High', 'Low', 'Close', 'Volume']] = self.data[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
                print(self.data.head())  # Print the first few rows of the DataFrame to inspect
            else:
                print("No kline data available for the specified date range.")
        else:
            print("Unexpected response structure:", response)
        
        return self.data

    def SetIndicator(self):
        if self.data is None or self.data.empty:
            raise ValueError("No data available to set indicators. Fetch data first.")
        if 'Close' not in self.data.columns:
            raise KeyError("The fetched data does not contain 'Close' column. Please check the data structure.")
        
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
        sessioninitial = TradingSession(api_key=creds.apikey, api_secret=creds.apisecret)  # Initialize session with API credentials
        for i in range(len(self.data)):
            if self.data['Signal'].iloc[i] == 1:
                print(f"Buy signal detected for {self.ticker}. Placing order.")
                sessioninitial.place_order()
            elif self.data['Signal'].iloc[i] == -1:
                print(f"Sell signal detected for {self.ticker}. Placing order.")
                sessioninitial.cancel_all_orders()

    def run_live_analysis(self):
        self.FetchData()
        self.SetIndicator()
        self.Fractal1()
        self.Fractal2()
        self.Fractal3()
        self.Fractal4()
        self.Divergence()
        self.Signal()
        self.execute_trades()
        # Add any other analysis or trading logic here

if __name__ == "__main__":
    api_key = creds.apikey
    api_secret_key = creds.apisecret
    bybit_client = TradingSession(api_key, api_secret_key)

    stocks = ['BTCUSDT', 'ETHUSDT', 'ETCUSDT', 'LTCUSDT', 'XRPUSDT', 'EOSUSDT']  # Add more symbols if needed
    for stock_symbol in stocks:
        stock_analysis = Strategy(stock_symbol, bybit_client)
        stock_analysis.run_live_analysis()
