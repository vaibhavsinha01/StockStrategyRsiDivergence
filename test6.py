import requests
import time
import hmac
import hashlib
import json  # Import the json module
from urllib.parse import urlencode


class Broker:
    @staticmethod
    def create_signature(api_secret, method, url, payload):
        secret_bytes = api_secret.encode('utf-8')
        message = (method + url + payload).encode('utf-8')  # Concatenate method, url, and payload
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

    # Update place_order method
    @staticmethod
    def place_order(symbol):
        method = "POST"
        url2 = "https://api-testnet.bybit.com/v5/order/create"

        timestamp = str(int(time.time() * 1000))
        payload = json.dumps({"symbol": "ETHUSDT", "side": "Buy", "order_type": "Limit", "qty": "1", "price": "1000"})  # Update payload to dict and serialize it
        signature = Broker.create_signature(secret, method, url2, payload)  # Use the serialized payload

        headers = {
            'X-BAPI-API-KEY': key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature
        }

        response = requests.post(url2, headers=headers, json=json.loads(payload))  # Deserialize payload and use json parameter instead of data
        print(response.text)

    # Update cancel_order method
    @staticmethod
    def cancel_order(symbol):
        method = 'POST'
        url3 = "https://api-testnet.bybit.com/v5/order/cancel"
        timestamp = str(int(time.time() * 1000))

        # Define the payload variable
        payload = {"symbol": symbol}  # Update payload to dict

        signature = Broker.create_signature(secret, method, url3, json.dumps(payload))  # Use json.dumps() to serialize the payload

        headers = {
            'X-BAPI-API-KEY': key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature
        }

        response = requests.post(url3, headers=headers, json=payload)  # Use json parameter instead of data
        print(response.text)

# Example usage
key = "yvbFHB7ghuq0tFQHOs"
secret = "8VRba94rVEd5MCcreRD96CPqx7bqmJrevf2p"

Broker.login(key, secret)
Broker.getkline("ETHUSDT")
Broker.get_ticker("ETHUSDT")
Broker.place_order("ETHUSDT")
Broker.cancel_order("ETHUSDT")
