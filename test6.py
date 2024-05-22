import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode

class Broker:
    @staticmethod
    def create_signature(api_secret, method, url, payload):
        secret_bytes = api_secret.encode('utf-8')
        message = (method + url + payload).encode('utf-8')
        signature = hmac.new(secret_bytes, message, hashlib.sha256).hexdigest()
        return signature

    @staticmethod
    def getkline(symbol):
        url1 = f"https://api-testnet.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=1"
        response = requests.get(url1)
        print(response.text)

    @staticmethod
    def login(api_key, api_secret):
        method = "POST"
        url = "https://api-testnet.bybit.com/v5/user/login"
        timestamp = str(int(time.time() * 1000))
        payload = f'{{"loginType": "api", "apiKey": "{api_key}", "timestamp": {timestamp}}}'
        signature = Broker.create_signature(api_secret, method, url, payload)

        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature
        }

        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            print("Login successful")
            return response.json()
        else:
            print("Login failed")
            return None

    @staticmethod
    def get_ticker(symbol):
        url = f"https://api-testnet.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
        response = requests.get(url)
        print(response.text)

    @staticmethod
    def place_order(symbol):
        method = "POST"
        url2 = "https://api-testnet.bybit.com/v5/order/create"

        timestamp = str(int(time.time() * 1000))
        payload = '{"category": "linear", "symbol": "ETHUSDT", "isLeverage": 0, "side": "Buy", "orderType": "Limit", "qty": "1", "price": "1000", "timeInForce": "GTC", "positionIdx": 0, "orderLinkId": "test-xx1"}'
        signature = Broker.create_signature(secret, method, url2, payload)

        headers = {
            'X-BAPI-API-KEY': key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature
        }

        response = requests.post(url2, headers=headers, data=payload)
        print(response.text)

    @staticmethod
    def cancel_order(symbol):
        method='POST'
        url3 = "https://api-testnet.bybit.com/v5/order/cancel"
        timestamp=str(int(time.time()*1000))

        # Define the payload variable
        payload = f'{{"category": "spot", "symbol": "{symbol}", "orderId": null, "orderLinkId": null, "orderFilter": "Order"}}'

        signature = Broker.create_signature(secret, method, url3, payload)

        headers = {
            'X-BAPI-API-KEY': key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature
        }

        response = requests.post(url3, headers=headers, data=payload)
        print(response.text)

# Example usage
key = "RpIwvnwYtPS380SxKV"
secret = "OP9SsrwYt9Y7Sveici9XjRucDtqBB0lqbY2C"

Broker.login(key, secret)
Broker.getkline("ETHUSDT")
Broker.get_ticker("ETHUSDT")
Broker.place_order("ETHUSDT")
Broker.cancel_order("ETHUSDT")
