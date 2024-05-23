from pybit.unified_trading import HTTP
import hashlib
import hmac
import requests
import time
from creds import secret,key

class BybitWrapper:
    def __init__(
            self,
            api_key:str=None,
            api_secret:str=None,
            testnet: bool=None
    ):
        self.instance=HTTP(
            api_key=api_key
            api_secret=api_secret
            testnet=testnet
            log_requests=True
        )

    def get_kline_data(self,symbol: str='BTCUSDT'):
        kline_data=self.instance.get_kline(
            category="linear"
            symbol=symbol
            interval=60
        )['result']

        data_list = kline_data["list"][0]

        print(f"Open price: {data_list[1]}")
        print(f"High price: {data_list[2]}")
        print(f"Low price: {data_list[3]}")
        print(f"Close price: {data_list[4]}")

    def cancel_all_orders(
            self,
            category:str,
            symbol:str=None,
    ) ->dict:
        
        return self.instance.get_open_orders(
            category=category,
            symbol=symbol
        )
    
    def get_realtime_orders(
        self,
        category: str,
        symbol: str = None,
    ) -> dict:
        """
        Get realtime orders
        """
        return self.instance.get_open_orders(
            category=category,
            symbol=symbol,
        )
    
    def get_order_history(self,**kwargs)->dict:
        return self.instance.get_order_history(**kwargs)["result"]["list"]
    
wrapper=BybitWrapper(
    api_key=key,
    api_secret=secret,
    testnet=TESTNET,
)

response=wrapper.get_realtime_orders(category="linear",symbol="ETHUSDT")