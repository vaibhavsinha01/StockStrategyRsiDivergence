class Broker:
    def __init__(self,balance):
        self.balance=balance
        self.stocks={}
    
    def buy_stock(self,symbol,quantity,price):
        cost=quantity*price
        if cost>self.balance:
            print("insufficient balance")
            return False
        
        else:
            if symbol in self.stocks:
                self.stocks[symbol] += quantity
            else:
                self.stocks[symbol] = quantity
            self.balance -= cost
            print(f"Bought {quantity} shares of {symbol} at ${price} each. Remaining balance: ${self.balance}")
            return True
        
    def sell_stock(self,symbol,quantity,price):
        if symbol not in self.stocks or self.stocks[symbol]<quantity:
            print("Not enough {} shares to sell.".format(symbol))
            return False
        else:
            self.stocks[symbol]-=quantity
            self.balance += quantity*price
            print("Sold {} shares of {} at ${} each. Remaining balance: ${}".format(quantity, symbol, price, self.balance))
            return True
        
    def get_balance(self):
        return self.balance

    def get_portfolio(self):
        return self.stocks
    
    
