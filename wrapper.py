from pybit.unified_trading import HTTP
import creds
import uuid

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
        
    def place_order(self, category="spot", symbol="BTCUSDT", side="Buy", orderType="Limit", qty="0.01", price="15600", timeInForce="PostOnly"):
    # Generate unique clientOrderId
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

trading_session = TradingSession()

# Example usage:
print(trading_session.account_balance())
print(trading_session.get_kline())
print(trading_session.orderbook())
print(trading_session.tickers())
print(trading_session.fee_rate_info())
print(trading_session.place_order())
print(trading_session.get_positions())
print(trading_session.cancel_all_orders())
print(trading_session.get_recent_trades())
print(trading_session.account_balance())
