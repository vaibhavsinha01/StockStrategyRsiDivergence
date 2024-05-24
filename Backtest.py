from backtesting import Backtest, Strategy
from backtesting.test import GOOG
from backtesting.lib import crossover, resample_apply
import talib

def optim_func(series):
    if series['# Trades'] < 10:
        return -1
    else:
        return series['Equity Final [$]'] / series['Exposure Time [%]']

class RsiOscillator(Strategy):
    upper_bound = 70
    lower_bound = 30
    rsi_window = 14

    def init(self):
        self.daily_rsi = self.I(talib.RSI, self.data.Close, self.rsi_window)
        self.weekly_rsi = resample_apply("W-FRI", talib.RSI, self.data.Close, self.rsi_window)

    def next(self):
        price = self.data.Close[-1]
        if crossover(self.daily_rsi, self.upper_bound):
            if self.position.is_long:
                self.position.close()
                self.sell()
        
        elif crossover(self.lower_bound, self.daily_rsi):
            if self.position.is_long or not self.position:
                self.position.close()
                self.buy(sl=0.95*price)

bt = Backtest(GOOG, RsiOscillator, cash=10000)

# Uncomment the following lines if you want to run optimization

stats = bt.optimize(
    upper_bound=range(50, 85, 5),
    lower_bound=range(15, 50, 5),
    rsi_window=range(12, 16, 1),
    maximize=optim_func,
    constraint=lambda param: param.lower_bound < param.upper_bound
)
print(stats)


# Run the backtest
stats = bt.run()

# Display the statistics
bt.plot()
