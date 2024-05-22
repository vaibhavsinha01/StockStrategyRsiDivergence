import requests
import time as time
from creds import secret, key
import hmac
import hashlib

class Broker:
    def create_signature(api_secret, method, url, payload):
        secret_bytes = api_secret.encode('utf-8')
        message = method.encode('utf-8') + url.encode('utf-8') + payload.encode('utf-8')
        signature = hmac.new(secret_bytes, message, hashlib.sha256).hexdigest()
        return signature

    def getkline(symbol):
        url1 = f"https://api-testnet.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=1"
        headers = {}
        response = requests.request("GET", url1, headers=headers)
        print(response.text)

    def login(api_key, api_secret):
        method = "POST"
        url = "https://api-testnet.bybit.com/v5/user/login"
        timestamp = str(int(time.time() * 1000))
        payload = "{\"loginType\": \"api\", \"apiKey\": \"" + api_key + "\", \"timestamp\": " + timestamp + "}"
        signature = Broker.create_signature(api_secret, method, url, payload)

        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            print("Login successful")
            return response.json()
        else:
            print("Login failed")
            return None

    def get_ticker(symbol):
        url = f"https://api-testnet.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
        payload = {}
        headers = {}
        response = requests.get(url, headers=headers, data=payload)
        print(response.text)

    def place_order(symbol):
        method = "POST"
        url2 = "https://api-testnet.bybit.com/v5/order/create"

        timestamp = str(int(time.time() * 1000))
        payload = "{\n  \"category\": \"linear\",\n  \"symbol\": \"ETHUSDT\",\n  \"isLeverage\": 0,\n  \"side\": \"Buy\",\n  \"orderType\": \"Limit\",\n  \"qty\": \"1\",\n  \"price\": \"1000\",\n  \"triggerPrice\": null,\n  \"triggerDirection\": null,\n  \"triggerBy\": null,\n  \"orderFilter\": null,\n  \"orderIv\": null,\n  \"timeInForce\": \"GTC\",\n  \"positionIdx\": 0,\n  \"orderLinkId\": \"test-xx1\",\n  \"takeProfit\": null,\n  \"stopLoss\": null,\n  \"tpTriggerBy\": null,\n  \"slTriggerBy\": null,\n  \"reduceOnly\": false,\n  \"closeOnTrigger\": false,\n  \"smpType\": null,\n  \"mmp\": null,\n  \"tpslMode\": null,\n  \"tpLimitPrice\": null,\n  \"slLimitPrice\": null,\n  \"tpOrderType\": null,\n  \"slOrderType\": null\n}"
        signature = Broker.create_signature(secret, method, url2, payload)

        headers = {
            'X-BAPI-API-KEY': 'a7zr474x6gRchvFiR0',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature
        }

        response = requests.request("POST", url2, headers=headers, data=payload)

        print(response.text)

    def cancel_order(symbol):
        method='POST'
        url3 = "https://api-testnet.bybit.com/v5/order/cancel"
        timestamp=str(int(time.time()*1000))

        # Define the payload variable
        payload = "{\n  \"category\": \"spot\",\n  \"symbol\": \"" + symbol + "\",\n  \"orderId\": null,\n  \"orderLinkId\": null,\n  \"orderFilter\": \"Order\"\n}"

        signature = Broker.create_signature(secret,method,url3,data=payload)

        headers = {
            'X-BAPI-API-KEY': 'a7zr474x6gRchvFiR0',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '200000',
            'X-BAPI-SIGN': signature
        }

        response = requests.request("POST", url3, headers=headers, data=payload)

        print(response.text)


Broker.login(key, secret)

# get klines
Broker.getkline("ETHUSDT")

# get ticker
Broker.get_ticker("ETHUSDT")

# place order
Broker.place_order("ETHUSDT")

