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
        print("BookSearch: LocalBookSearch for books with")
        print(f"\tISBN: {self.ISBN}")
        print(f"\tAuthor: {self.author}")
        print(f"\tTitle: {self.title}")
        # Check against any ISBN matches
        results = self._check_local_isbn()

        # Check against author and title matches combined
        results += self._check_local_author_and_title()

        print(results)

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
        Checks UserBooks table for ISBN
        """
        books_isbn_results = []
        books_isbn = self.bsdb.check_ISBN(self.ISBN)
        for book in books_isbn:
            books_isbn_results.append(self._process_results_row(book))
        return books_isbn_results

    def _check_local_author_and_title(self):
        """
        Checks UserBooks table for author and title matches
        """
        books_author_and_title_results = []
        books_author_and_title = self.bsdb.check_author_and_title(self.author,
                self.title)
        for book in books_author_and_title:
            books_author_and_title_results.append(self._process_results_row(book))
        return books_author_and_title_results
    
