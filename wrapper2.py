import requests
import time
import hmac
import hashlib
import json
import creds  # Ensure this file contains your secret and key securely

class Broker:
    api_key = creds.apikey
    api_secret = creds.apisecret

    @staticmethod
    def create_signature(api_secret, method, url, payload):
        secret_bytes = api_secret.encode('utf-8')
        message = f'{method}{url}{payload}'.encode('utf-8')
        signature = hmac.new(secret_bytes, message, hashlib.sha256).hexdigest()
        return signature

    @staticmethod
    def getkline(symbol):
        url = f"https://api-testnet.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=1"
        response = requests.get(url)
        response_json = response.json()
        print(response_json)
        

    @staticmethod
    def login(api_key, api_secret):
        method = "POST"
        url = "https://api-testnet.bybit.com/v5/user/login"
        timestamp = str(int(time.time() * 1000))
        payload = json.dumps({
            "loginType": "api",
            "apiKey": api_key,
            "timestamp": timestamp
        })
        signature = Broker.create_signature(api_secret, method, url, payload)

        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload)
        print(f"Login request: {response.request.body}")
        print(f"Login headers: {response.request.headers}")
        response_json = response.json()
        if response.status_code == 200:
                print("Login successful")
                return response_json
        else:
                print("Login failed:", response_json)
                return response_json

    @staticmethod
    def get_ticker(symbol):
        url = f"https://api-testnet.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
        response = requests.get(url)
        response_json = response.json()
        print(response_json)

    @staticmethod
    def place_order(symbol):
        method = "POST"
        url = "https://api-testnet.bybit.com/v5/order/create"

        timestamp = str(int(time.time() * 1000))
        payload = json.dumps({
            "category": "linear",
            "symbol": symbol,
            "isLeverage": 0,
            "side": "Buy",
            "orderType": "Limit",
            "qty": "1",
            "price": "1000",
            "timeInForce": "GTC",
            "positionIdx": 0,
            "orderLinkId": "test-xx1"
        })
        signature = Broker.create_signature(creds.apisecret, method, url, payload)

        headers = {
            'X-BAPI-API-KEY': creds.apikey,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)
        print(f"Place order request: {response.request.body}")
        print(f"Place order headers: {response.request.headers}")
        
        response_json = response.json()
        print(response_json)
        

    @staticmethod
    def cancel_order(symbol):
        method = "POST"
        url = "https://api-testnet.bybit.com/v5/order/cancel"
        timestamp = str(int(time.time() * 1000))
        payload = json.dumps({
            "category": "spot",
            "symbol": symbol,
            "orderId": None,
            "orderLinkId": None,
            "orderFilter": "Order"
        })

        signature = Broker.create_signature(creds.apisecret, method, url, payload)

        headers = {
            'X-BAPI-API-KEY': creds.apikey,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)
        print(f"Cancel order request: {response.request.body}")
        print(f"Cancel order headers: {response.request.headers}")
        response_json = response.json()
        print(response_json)
        

# Login
login_response = Broker.login(creds.apikey, creds.apisecret)

# Get klines
Broker.getkline("ETHUSDT")

# Get ticker
Broker.get_ticker("ETHUSDT")

# Place order
Broker.place_order("ETHUSDT")

# Cancel order (provide a valid symbol and optionally orderId or orderLinkId)
Broker.cancel_order("ETHUSDT")
