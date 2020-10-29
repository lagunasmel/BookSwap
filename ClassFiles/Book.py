class Book:
    def __init__(self, title, isbn):
        self._title = title
        self._isbn = isbn

    def get_title(self):
        return self._title

    def get_isbn(self):
        return self._isbn


