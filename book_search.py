from db_connector import get_db, BookSwapDatabase


class BookSearch:
    """
    BookSearch contains the structure and methods for performaing a book search.
    """

    def __init__(self, search_query, bsdb):
        """
        Class initializer.  Sets search query and database object for use.
        Accepts:
            search_query (tuple of string):  Search query from user, in 
                (ISBN, author, title) format
            bsdb (BookSwapDatabase instance): database access object
        """
        self.ISBN = search_query[0]
        self.author = search_query[1]
        self.title = search_query[2]
        self.bsdb = bsdb

    def local_book_search(self, num):
        """
        Book_Search looks in Books table to locate books that satisfy the 
            search.
        Accepts:
            num (int): Desired number of results
        Returns:
            list of dictionaries
        """
        # Check against any ISBN matches
        results = self._check_local_isbn()

        return results

    def _process_results_row(self, row):
        """
        Process a row object returned from SQLite database, creating a
            dictionary.
        Accepts:
            row (SQLite Row object): Row from SQLite3 query result
        Returns:
            Dictionary with keys: id, ISBN, author, title, externalLink
        """
        response_dict = dict()
        for key in row.keys():
            response_dict[key] = row[key]
        return response_dict

    def _check_local_isbn(self):
        """
        Checks Books table for ISBN
        """
        books_isbn_results = []
        books_isbn = self.bsdb.check_ISBN(self.ISBN)
        for book in books_isbn:
            books_isbn_results.append(self._process_results_row(book))
        return books_isbn_results
