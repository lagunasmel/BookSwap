class Trade:
    def __init__(self, book, seller, price):
        self._book = book
        self._seller = seller
        self._price = price
        self._buyer = None

    def set_buyer(self, buyer):
        self.buyer = buyer

    def get_seller(self):
        return self._seller

    def get_price(self):
        return self._price

    def get_buyer(self):
        return self._buyer

    def get_book(self):
        return self._book

    def trade_book(self):
        pass
    
    def reject_trade(self):
        # User rejects trade, trade should disappear
