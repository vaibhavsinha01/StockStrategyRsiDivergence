import requests
import time as time
from creds import secret,key

# a function for getting kline
def getkline(symbol):
    url1 = f"https://api-testnet.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=1"
    headers = {}

    response = requests.request("GET", url1, headers=headers)

    print(response.text)
# a function to login

def login(s,k):
  if (s==secret) & (k==key):
    print("login is successful")
  else:
    print("login is unsuccessful")

# a function for placing an order

def place_order():
  url2 = "https://api-testnet.bybit.com/v5/order/create"

  timestamp=str(int(time.time()*1000))

  payload = "{\n  \"category\": \"linear\",\n  \"symbol\": \"ETHUSDT\",\n  \"isLeverage\": 0,\n  \"side\": \"Buy\",\n  \"orderType\": \"Limit\",\n  \"qty\": \"1\",\n  \"price\": \"1000\",\n  \"triggerPrice\": null,\n  \"triggerDirection\": null,\n  \"triggerBy\": null,\n  \"orderFilter\": null,\n  \"orderIv\": null,\n  \"timeInForce\": \"GTC\",\n  \"positionIdx\": 0,\n  \"orderLinkId\": \"test-xx1\",\n  \"takeProfit\": null,\n  \"stopLoss\": null,\n  \"tpTriggerBy\": null,\n  \"slTriggerBy\": null,\n  \"reduceOnly\": false,\n  \"closeOnTrigger\": false,\n  \"smpType\": null,\n  \"mmp\": null,\n  \"tpslMode\": null,\n  \"tpLimitPrice\": null,\n  \"slLimitPrice\": null,\n  \"tpOrderType\": null,\n  \"slOrderType\": null\n}"
  headers = {
      'X-BAPI-API-KEY': 'CFEJUGQEQPPHGOHGHM',
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
    'X-BAPI-API-KEY': 'CFEJUGQEQPPHGOHGHM',
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
    'X-BAPI-API-KEY': 'CFEJUGQEQPPHGOHGHM',
    'X-BAPI-TIMESTAMP': timestamp,
    'X-BAPI-RECV-WINDOW': '20000',
    'X-BAPI-SIGN': '7edaae594e3e331689a740ff70f5be0da00aa72bfac1d37c7046083365b4a42a'
  }

  response = requests.request("GET", url4, headers=headers, data=payload)

  print(response.text)

# a function for getting the order history

def get_order_history():
  url5 = "https://api-testnet.bybit.com/v5/order/history"
  timestamp=str(int(time.time()*1000))
  payload={}
  headers = {
    'X-BAPI-API-KEY': 'CFEJUGQEQPPHGOHGHM',
    'X-BAPI-TIMESTAMP': timestamp,
    'X-BAPI-RECV-WINDOW': '20000',
    'X-BAPI-SIGN': '654e662d29f22fba724bcf2e24d612fcaa4c1b38027d9838a226032c37429680'
  }

  response = requests.request("GET", url5, headers=headers, data=payload)

  print(response.text)

# a function for getting balance of all coins

def get_balance_coins():
  url6 = "https://api-testnet.bybit.com/v5/asset/transfer/query-account-coins-balance?accountType=INVESTMENT"
  timestamp=str(int(time.time()*1000))
  payload={}
  headers = {
      'X-BAPI-API-KEY': 'FzOqnkUUopI7emsDJ8',
      'X-BAPI-TIMESTAMP': timestamp,
      'X-BAPI-RECV-WINDOW': '20000',
      'X-BAPI-SIGN': '880fe4de0a5998eab1178e7292b77573001d70311c76db93adb2e013f23603df'
    }

  response = requests.request("GET", url6, headers=headers, data=payload)

  print(response.text)

# a function to set up the takeprofit and stoploss mode

def set_SLandTP():
  url7 = "https://api-testnet.bybit.com/v5/position/set-tpsl-mode"
  timestamp=str(int(time.time()*1000))

  payload = "{\n  \"category\": \"linear\",\n  \"symbol\": \"ETHUSDT\",\n  \"tpSlMode\": \"Full\"\n}"
  headers = {
    'X-BAPI-API-KEY': 'CFEJUGQEQPPHGOHGHM',
    'X-BAPI-TIMESTAMP': timestamp,
    'X-BAPI-RECV-WINDOW': '20000',
    'X-BAPI-SIGN': '8893f51353b36d96122c1fa8217ec378cd5ece0984f3f6708413fe90c65263ec'
  }

  response = requests.request("POST", url7, headers=headers, data=payload)

  print(response.text)

# a function to get account information

def get_account_information():
  url8 = "https://api-testnet.bybit.com/v5/account/info"
  timestamp=str(int(time.time()*1000))
  payload={}
  headers = {
    'X-BAPI-API-KEY': 'CFEJUGQEQPPHGOHGHM',
    'X-BAPI-TIMESTAMP': timestamp,
    'X-BAPI-RECV-WINDOW': '20000',
    'X-BAPI-SIGN': '3d7b7c288edde8914e90e65aec4d1fbc848ea125bae623f3fdd223f54a6a4ec4'
  }

  response = requests.request("GET", url8, headers=headers, data=payload)

  print(response.text)

def main():
  login("5tOGM14Ek0YUXkyWd033OZzyz6pUA5yPvtIa","a7zr474x6gRchvFiR0")
  getkline("BTCUSDT")
  place_order()
  set_SLandTP()
  cancel_order()
  get_balance()
  get_order_history()
  get_account_information()
  
main()




