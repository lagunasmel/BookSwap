from Trade import Trade
from Book import Book

class BookUser:
    def __init__(self, name, identifier):
        self._books = []
        self._name = name
        self._id = identifier
        self._trades = []
        self._points = 0
    
    def post_book(self, book, price):
        # New trade object -- id probably better than name for this?
        newTrade = Trade(book, self._id, price)
        self._trades.append(newTrade)

        # Should also put this new book in the marketplace
    
    def get_books(self):
        return self._books

    def get_name(self):
        return self._name

    def get_id(self):
        return self._id

    def get_trades(self):
        # Not sure this is really valuable
        return self._trades

    def get_points(self):
        return self._points

    def change_points(self, modifier):
        self._points += modifier
