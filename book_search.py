from db_connector import BookSwapDatabase


class BookSearch:
    """
    BookSearch contains the structure and methods for performaing a book search.
    """

    def __init__(self, search_query, bsdb: BookSwapDatabase):
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

    def combined_book_search(self, num_local, num_external):
        """
        Searches for matching books, both locally and online from the OpenLibrary API.

        :param num_local: number of results to return from the books already listed by users
        :param num_external: number of results to return from the open library API - will never include any local result

        :return: a tuple (local_results, external_results)
        """
        local_results = self.local_book_search(num_local)
        book_id_ignorelist = [r['booksId'] for r in local_results]
        external_results = self.bsdb.search_books_openlibrary(self.title, self.author, self.ISBN, num_external,
                                                              book_id_ignorelist=book_id_ignorelist)
        return local_results, external_results

    def local_book_search(self, num):
        """
        Book_Search looks in Books table to locate books that satisfy the 
            search.
        Accepts:
            num (int): Desired number of results
        Returns:
            list of dictionaries including the keys: 'title', 'author', 'ISBN', 'copyQuality', 'userId',
            'pointsNeeded', 'userBooksId', 'booksId'
        """
        print("BookSearch: LocalBookSearch for books with")
        print(f"\tISBN: {self.ISBN}")
        print(f"\tAuthor: {self.author}")
        print(f"\tTitle: {self.title}")
        # Check against any ISBN matches
        results = self._check_local_isbn()

        # Check against author and title matches combined
        author_and_title = self._check_local_author_and_title()
        results = self._results_combine(results, author_and_title)

        # Check against author or title matches
        author_or_title = self._check_local_author_or_title()
        results = self._results_combine(results, author_or_title)

        for result in results:
            print(result)

        return results[:num]

    def _results_combine(self, results, new_results):
        """
        Combines the second list to the first, avoiding books with identical 
            "UserBooks.id" values.
        Accepts:
            results (list of dicts): Original list
            new_results (list of dicts): New list to append
        Returns:
            None, but results is mutated.
        """
        id_list = [result["UserBooksId"] for result in results]
        for new_result in new_results:
            if new_result.get("UserBooksId", 0) not in id_list:
                results.append(new_result)
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
        books_isbn = self.bsdb.get_books_by_ISBN(self.ISBN)
        for book in books_isbn:
            books_isbn_results.append(self._process_results_row(book))
        return books_isbn_results

    def _check_local_author_and_title(self):
        """
        Checks UserBooks table for author and title matches
        """
        books_author_and_title_results = []
        books_author_and_title = self.bsdb.get_books_by_author_and_title(self.author,
                                                                         self.title)
        for book in books_author_and_title:
            books_author_and_title_results.append(self._process_results_row(book))
        return books_author_and_title_results

    def _check_local_author_or_title(self):
        """
        Checks UserBooks table for author or title matches
        """
        books_author_or_title_results = []
        books_author_or_title = self.bsdb.get_books_by_author_or_title(self.author,
                                                                       self.title)
        for book in books_author_or_title:
            books_author_or_title_results.append(self._process_results_row(book))
        return books_author_or_title_results
