import requests
import time
from creds import key, secret, login, password

url1 = "https://api-testnet.bybit.com/v5/order/create"
url2 = "https://api-testnet.bybit.com/v5/order/cancel"

class ByBitBroker:
    def __init__(self, balance):
        self.balance = balance
        self.stocks = {}

    def login(self, user, password1, k, secr):
        if user == login and password1 == password and k == key and secr == secret :
            print("Successfully logged in")
        else:
            print("Login unsuccessful")
    
    def place_order(self, quantity, symbol):
        header = self.get_default_header()
        payload = {
            "category": "linear",
            "symbol": symbol,
            "qty": quantity,
        }
        response = requests.post(url1, headers=header, json=payload)
        print(response.text)  
    
    def cancel_order(self, order_id):
        header = self.get_default_header()
        payload = {
            "orderId": order_id,
        }
        response = requests.post(url2, headers=header, json=payload)
        print(response.text)  

    def get_stocks(self):
        return self.stocks
    
    def get_balance(self):
        return self.balance

    def get_default_header(self):
        current_timestamp = str(int(time.time() * 1000))  
        return {
            'X-BAPI-API-KEY': key,
            'X-BAPI-TIMESTAMP': current_timestamp,  
            'X-BAPI-RECV-WINDOW': '2000', 
            'X-BAPI-SIGN': 'd97c47798adf11dffcf16c292d56fc1e594a5a4f45a4a0137b3ba384c0ac026a'
        }

    
