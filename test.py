import requests
import time as time
from creds import secret,key
from pybit.unified_trading import HTTP
import hmac
import hashlib

#things to do 

#1)put this in broker class 2)set the parameters for the payload 3)write using init function 4)get correct timestamp 5)ask to get the correct api key
#6)set the login funcion correctly


def getkline(symbol):
    url1 = f"https://api-testnet.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=1"
    headers = {}
    response = requests.request("GET", url1, headers=headers)
    print(response.text)

def login(s,k):
  if (s==secret) & (k==key):
    print("login is successful")
  else:
    print("login is unsuccessful")

def get_ticker(symbol):
    url = f"https://api-testnet.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
    payload = {}
    headers = {}
    response = requests.get(url, headers=headers, data=payload)
    print(response.text)


# a function for placing an order

def place_order():
  url2 = "https://api-testnet.bybit.com/v5/order/create"

  timestamp=str(int(time.time()*1000))

  payload = "{\n  \"category\": \"linear\",\n  \"symbol\": \"ETHUSDT\",\n  \"isLeverage\": 0,\n  \"side\": \"Buy\",\n  \"orderType\": \"Limit\",\n  \"qty\": \"1\",\n  \"price\": \"1000\",\n  \"triggerPrice\": null,\n  \"triggerDirection\": null,\n  \"triggerBy\": null,\n  \"orderFilter\": null,\n  \"orderIv\": null,\n  \"timeInForce\": \"GTC\",\n  \"positionIdx\": 0,\n  \"orderLinkId\": \"test-xx1\",\n  \"takeProfit\": null,\n  \"stopLoss\": null,\n  \"tpTriggerBy\": null,\n  \"slTriggerBy\": null,\n  \"reduceOnly\": false,\n  \"closeOnTrigger\": false,\n  \"smpType\": null,\n  \"mmp\": null,\n  \"tpslMode\": null,\n  \"tpLimitPrice\": null,\n  \"slLimitPrice\": null,\n  \"tpOrderType\": null,\n  \"slOrderType\": null\n}"
  headers = {
      'X-BAPI-API-KEY': 'a7zr474x6gRchvFiR0',
      'X-BAPI-TIMESTAMP': timestamp,
      'X-BAPI-RECV-WINDOW': '20000',
      'X-BAPI-SIGN': '4d7e04a9ea32141613b6c0ca85b552b65ff50f302cc0d74c72382242ebe34c11'
      }

  response = requests.request("POST", url2, headers=headers, data=payload)

  print(response.text)


# a function for cancelling an order

def cancel_order():
  url3 = "https://api-testnet.bybit.com/v5/order/cancel"
  timestamp=str(int(time.time()*1000))

  payload = "{\n  \"category\": \"spot\",\n  \"symbol\": \"ETHUSDT\",\n  \"orderId\": null,\n  \"orderLinkId\": null,\n  \"orderFilter\": \"Order\"\n}"
  headers = {
    'X-BAPI-API-KEY': 'a7zr474x6gRchvFiR0',
    'X-BAPI-TIMESTAMP': timestamp,
    'X-BAPI-RECV-WINDOW': '20000',
    'X-BAPI-SIGN': 'd2e9a3da3bbcdf5cf14b041049523b9bb5cb5dd80f6c58ef97a27a4c676a39c2'
  }

  response = requests.request("POST", url3, headers=headers, data=payload)

  print(response.text)

# a function for getting the balance

def get_balance():
  url4 = "https://api-testnet.bybit.com/v5/account/wallet-balance"

  payload={}

  timestamp=str(int(time.time()*1000))
  print(timestamp)

  headers = {
    'X-BAPI-API-KEY': 'a7zr474x6gRchvFiR0',
    'X-BAPI-TIMESTAMP': timestamp,
    'X-BAPI-RECV-WINDOW': '20000',
    'X-BAPI-SIGN': '7edaae594e3e331689a740ff70f5be0da00aa72bfac1d37c7046083365b4a42a'
  }

  response = requests.request("GET", url4, headers=headers, data=payload)

  print(response.text)

# a function to get account information

def get_account_information():
  url8 = "https://api-testnet.bybit.com/v5/account/info"
  timestamp=str(int(time.time()*1000))
  payload={}
  headers = {
    'X-BAPI-API-KEY': 'a7zr474x6gRchvFiR0',
    'X-BAPI-TIMESTAMP': timestamp,
    'X-BAPI-RECV-WINDOW': '20000',
    'X-BAPI-SIGN': '3d7b7c288edde8914e90e65aec4d1fbc848ea125bae623f3fdd223f54a6a4ec4'
  }

  response = requests.request("GET", url8, headers=headers, data=payload)

  print(response.text)

def main():
  login("5tOGM14Ek0YUXkyWd033OZzyz6pUA5yPvtIa","a7zr474x6gRchvFiR0")
  getkline("BTCUSDT")
  get_ticker("BTCUSDT")
  place_order()
  cancel_order()
  get_balance()
  get_account_information()

main()




