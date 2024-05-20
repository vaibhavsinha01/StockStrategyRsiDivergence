import requests
from creds import key, secret, login, password

url = "https://api-testnet.bybit.com/v5/order/create"

class ByBitBroker:
    def __init__(self, balance):
        self.balance = balance
        self.stocks = {}

    def login(user, password, k, secr):
        if user == login and password == password and k == key and secr == secret:
            print("Successfully logged in")
        else:
            print("Login unsuccessful")
    
    def place_order(self, quantity, symbol):
        header = {
            'X-BAPI-API-KEY': key,
            'X-BAPI-TIMESTAMP': '1716201412259', 
            'X-BAPI-RECV-WINDOW': '20000',
            'X-BAPI-SIGN': 'd97c47798adf11dffcf16c292d56fc1e594a5a4f45a4a0137b3ba384c0ac026a'
        }
        payload = {
            "category": "linear",
            "symbol": symbol,
            "qty": quantity,
        }
        response = requests.post(url, headers=header, json=payload)
        print(response.text)  
    
    def cancel_order(self, order_id):
        header = {
            'X-BAPI-API-KEY': key,
            'X-BAPI-TIMESTAMP': '1716201412259',  
            'X-BAPI-RECV-WINDOW': '20000',
            'X-BAPI-SIGN': 'd97c47798adf11dffcf16c292d56fc1e594a5a4f45a4a0137b3ba384c0ac026a'
        }
        payload = {
            "orderId": order_id,
        }
        response = requests.post(url, headers=header, json=payload)
        print(response.text)  

    def get_stocks(self):
        return self.stocks
