from backtesting import Backtest, Strategy
from backtesting.test import GOOG
from backtesting.lib import crossover, resample_apply
import talib
import numpy as np

def optimfunc(series):
    if series["# Trades"] < 10:
        return -1
    else:
        return series['Equity Final [$]']

class Backtesting(Strategy):
    upper_bound_rsi=70
    lower_bound_rsi=30
    rsi_window=14
    bb_window=14
    stlo=97
    tkpr=110

    def init(self):
        self.daily_rsi = self.I(talib.RSI, self.data.Close, self.rsi_window)
        self.volume_delta = np.diff(self.data.Volume) 
        self.bollinger_upper, self.bollinger_middle, self.bollinger_lower = self.I(
            talib.BBANDS, self.data.Close,timeperiod=self.bb_window)
        
    def next(self):
        price=self.data.Close
        if (self.daily_rsi < self.lower_bound_rsi and self.data.Close < self.bollinger_middle):
            if self.position.is_long:
                self.position.close()
                self.buy(sl=(self.stlo*price)/100,tp=(self.tkpr*price)/100)
        elif (self.daily_rsi > self.upper_bound_rsi and self.data.Close > self.bollinger_middle):
            if self.position.is_short or not self.position:
                self.position.close()
                self.buy(sl=(self.stlo*price)/100,tp=(self.tkpr*price)/100)

        
bt = Backtest(GOOG, Backtesting, cash=10000)

stats=bt.optimize(
    upper_bound_rsi=range(50,85,5),
    lower_bound_rsi=range(15,50,5),
    rsi_window=range(12,16,1),
    bb_window=range(12,16,1),
    stlo=range(95,99,1),
    tkpr=range(105,115,1),
    maximize=optimfunc,
    constraint=lambda param:param.lower_bound_rsi<=param.upper_bound_rsi
)

bt.plot()

