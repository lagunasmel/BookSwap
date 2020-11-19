import sqlite3
from flask import g, session, redirect, url_for
import requests

DATABASE = 'DatabaseSpecs/test-db.db'


def get_db():
    """
    get_db opens the connection to the Sqlite database file.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


class BookSwapDatabase:
    """
    This class is intended to deal with everything-SQL related:
        opening and closing connections to the database
        running queries and returning the results
        adding/deleting rows given criteria

    So that the routes in app.py don't have to touch the SQL themselves,
    and repeated functionality can be consolidated here
    """

    def __init__(self):
        self.db = get_db()
        self.db.row_factory = sqlite3.Row  # This allows us to access values by column name later on

    def close(self):
        """
        Closes the db connection
        :return: Nothing
        """
        self.db.close()

    def get_account_settings(self, user_id):
        """
        Gets account settings for a given user.
        Returned as a sqlite3.Row which can be accessed by key.
        """
        c = self.db.cursor()
        c.execute("""SELECT 
                    username, 
                    email,
                    fName, 
                    lName, 
                    streetAddress, 
                    city, 
                    state, 
                    postCode, 
                    points 
                FROM Users WHERE id=?;""", (user_id,))
        rows = c.fetchall()
        if len(rows) == 0:
            session.clear()
            return redirect(url_for('login'))
        if len(rows) > 1:
            raise KeyError("User ID did not return only one row")
        return rows[0]

    def get_book_qualities(self):
        """
        Returns a list of tuples containing (quality ID, copy quality description)
        :return: dict
        """
        c = self.db.cursor()
        c.execute("""SELECT id, qualityDescription FROM CopyQualities;""")
        rows = c.fetchall()
        out = []
        for row in rows:
            out.append((row["id"], row["qualityDescription"]))
        return out

    def get_listed_books(self, user_num):
        """
        Returns the rows corresponding to the books that user_id has listed as
        available for swapping.
        :param user_num: the ID of the user whose listed books to return
        :return: a list of sqlite3.Row objects corresponding to the listed books
        """
        c = self.db.cursor()
        c.execute("""
                    SELECT 
                        B.title AS Title, 
                        B.ISBN AS ISBN, 
                        B.author AS Author, 
                        CQ.qualityDescription AS Quality,
                        UB.id AS id 
                        FROM 
                            UserBooks UB 
                        INNER JOIN 
                            Books B on UB.bookId = B.id 
                        INNER JOIN 
                        CopyQualities CQ ON UB.copyQualityId = CQ.id 
                        WHERE 
                            userId = ?
                        AND
                            UB.available == 1
                    """,
                  (user_num,))
        rows = c.fetchall()
        self.db.commit()
        return rows

    def get_userBooksID(self, user_num):
        """
        Returns the UserBooks.id attribute for each of the user's books
        """

        c = self.db.cursor()
        c.execute("""SELECT id FROM UserBooks WHERE userId=?""", (user_num,))
        rows = c.fetchall()
        self.db.commit()
        return rows

    def get_trade_info(self, user_num):

        c = self.db.cursor()
        c.execute("""
                SELECT  Trades.statusId StatusId,
                        Trades.dateInitiated AS StartDate,
                        Books.title AS Title,
                        Books.author AS Author,
                        CopyQualities.qualityDescription AS Quality,
                        UserBooks.points AS Points,
                        U1.username AS Owner,
                        U2.username AS Requester
                FROM    Users U1 INNER JOIN
                        UserBooks on U1.id = UserBooks.userId INNER JOIN
                        Trades on UserBooks.id = Trades.userBookId INNER JOIN
                        Books on Books.id = UserBooks.bookId INNER JOIN
                        CopyQualities ON UserBooks.CopyQualityId = CopyQualities.Id INNER JOIN
                        Users U2 on U2.id = Trades.userRequestedId
                WHERE
                        UserBooks.userId = ?
                """, (user_num,))
        rows = c.fetchall()
        self.db.commit()

        return rows

    def get_or_add_ol_book_details(self, search_result):
        """
        Does the same thing as get_ol_book_details, but if the book is not yet stored then finds the first english
        language paperback/hardcover Edition of the Work corresponding to the given key in the Open Library API and
        then inserts its details into the Books table.

        To do this a dict called 'search result' corresponding to the JSON search result returned by Open Library is
        required. To clarify: there is currently no way to add details for an Open Library Work, given a Work Key,
        unless we have access to the information from the search result.  

        :param editions: a list of Open Library keys for Editions corresponding to the given Work
        :returns a dict of the attributes for the Books row
        """
        # Get the Work Key from the search result
        work_key = search_result['key'].split('/')[2]

        # First check if it exists
        local = self.get_ol_book_details(work_key)
        if local is not None:
            return local

        # Get the info of the first printed, english-language, edition, to store
        d = {'title': search_result['title'], 'author': search_result['author_name'][0], 'OLWorkKey': work_key}
        editions = search_result['edition_key']

        # Check the editions 10 at a time
        n = len(editions)
        edition_key = None
        isbn = None
        i = 0
        while (i < (n // 10) + 1) and (edition_key is None):
            batch = editions[i:i + 10]
            url = 'https://openlibrary.org/api/books'
            payload = {'format': 'json',
                       'jscmd': 'details',
                       'bibkeys': ','.join(batch)}
            r = requests.get(url, params=payload)
            data = r.json()
            for candidate in data.keys():
                details = data[candidate]['details']
                if 'languages' in details and 'covers' in details and 'isbn_13' in details:
                    languages = details['languages']
                    if len(languages) == 1 and languages[0]['key'] == '/languages/eng':
                        edition_key = candidate
                        isbn = int(details['isbn_13'][0])
                        break
            i += 10

        # Note that edition_key could still be None if we didn't find a suitable one, that's fine
        # Insert the book info now
        d['OLEditionKey'] = edition_key
        d['ISBN'] = isbn
        if edition_key is not None:
            d['coverImageUrl'] = "http://covers.openlibrary.org/b/olid/" + edition_key + "-L.jpg"
        else:
            d['coverImageUrl'] = None
        c = self.db.cursor()
        c.execute(
            """INSERT INTO Books (title, author, ISBN, OLWorkKey, OLEditionKey, coverImageUrl) VALUES (?, ?, ?, ?, ?, 
            ?)""",
            (d['title'], d['author'], isbn, work_key, edition_key, d['coverImageUrl']))
        self.db.commit()
        d['id'] = c.lastrowid  # ID of the recently inserted Books row
        return d

    def get_ol_book_details(self, work_key):
        """
        Returns the Books table attributes for a given Work, as defined by Open Library. If the volume has not yet
        been locally stored in the database, None is returned, and 'get_or_add_ol_book_details' must be called instead.

        :param work_key: the Open Library Works Key (eg 'OL27448W') associated with the volume.

        :returns a sqlite Row or a dict of the Book's attributes, with the keys: 'id', 'title', 'author', 'isbn',
        'OLEditionKey', 'OLWorkKey'
        """
        c = self.db.cursor()
        c.execute(
            """SELECT id, title, author, ISBN, OLWorkKey, OLEditionKey, coverImageUrl FROM Books WHERE OLWorkKey=?""",
            (work_key,))
        rows = c.fetchall()
        if len(rows) > 1:
            # This should not happen!
            raise LookupError(
                "Multiple Books found to correspond to a single work key - this should never "
                "happen!")
        elif len(rows) == 1:
            return rows[0]
        elif len(rows) == 0:
            # Book does not exist - must call 'get_or_add_ol_book_details' with a list of Edition keys
            return None

    def search_books_openlibrary(self, title=None, author=None, isbn=None, num_results=1):
        """
        Searches for books that match the provided details, and then returns the results. The search is conducted on
        the Open Library API. This method automatically searches for matching books and stores a local copy of the
        details in the Books table if it does not exist. What is returned is easy to work with:
        a list of sqlite.Row objects corresponding to selections from the Books table, so all the keys
        are the names of attributes of the Books table.

        Example:
        result = search_books_openlibrary(title="Lord", author="Tolkien", num_results=1)
        book_id = result[0]['id']
        image_url = result[0]['coverImageUrl']

        Open Library works by creating a 'Work' for each book, which has a 1:M relationship
        with 'Editions'. For example, the first Harry Potter book is a single 'Work' corresponding to 191 'Editions'
        that come in different languages and formats. Here we fetch some details from the Work (author, title) and
        others from the Edition - using the first English paperback/hardback edition.

        :param title: String, search is done for books whose title contains this
        :param author: Search is done for books whose author contains this string
        :param isbn: Must be a STRING
        :param num_results: int, the number of results to return

        :returns A 'num_results' long list of dicts/sqlite.Rows corresponding to search results.
                    Each row has the following keys:
                    'id' - from the Books table
                    'title'
                    'OLWorkKey' (a unique open library key for the work - not a specific edition)
                    'OLEditionKey' (as above, but for a specific edition - could be None if no suitable edition found)
                    'author'
                    'coverImageUrl'
        """
        # Get the search results
        url = "http://openlibrary.org/search.json"
        if title == '':
            title = None
        if author == '':
            author = None
        payload = {'title': title, 'author': author, 'isbn': isbn}
        r = requests.get(url, params=payload)  # auto-ignores 'None' values
        if r.status_code != 200:
            results = []
        else:
            results = r.json()['docs'][:num_results]
        out = []

        # Return the book info
        for result in results:
            book_info = self.get_or_add_ol_book_details(result)  # This does the heavy lifting
            out.append(book_info)

        return out

    def user_add_book_by_id(self, book_id, user_num, copyquality):
        """
        'user_id' user lists the book matching 'id' as available to swap.
        Nothing happens on failure.
        """
        c = self.db.cursor()
        c.execute("""INSERT INTO UserBooks (userId, bookId, copyQualityId) VALUES (?, ?, ?)""",
                  (user_num, book_id, copyquality))
        self.db.commit()
        return

    def user_add_book_by_isbn(self, isbn, user_num, copyquality):
        """
        'user_id' user lists the book matching 'isbn' as available to swap.
        Nothing happens on failure.

        This method delegates the job of getting the Books.id value for a given volume to another method,
        and only deals with the job of creating the required UserBooks entry. It is that other method that interfaces
        with the Google Books API.

        :param copyquality: ID corresponding to the quality of the book copy
        :param user_num: database ID of the user to add the book to
        :param isbn: ISBN of the book to be listed as available to swap
        :return: Nothing
        """
        self.db.row_factory = sqlite3.Row  # This allows us to access values by column name later on
        c = self.db.cursor()
        # First get book ID
        c.execute("""SELECT id FROM Books WHERE ISBN=?""", (isbn,))
        rows = c.fetchall()
        # TODO handle multiple matches better
        if len(rows) != 1:
            print("Warning: no matching book found when trying to list a book")
            return
        book_id = rows[0]["id"]
        c.execute("""INSERT INTO UserBooks (userId, bookId, copyQualityId) VALUES (?, ?, ?)""",
                  (user_num, book_id, copyquality))
        self.db.commit()

    def is_username_available(self, username):
        """
        Checks if username is not yet taken in database.
        Accepts:
            username (string): Username we are checking for
        Returns:
            True if username is not yet used, false if it is already used.
        """
        c = self.db.cursor()
        c.execute("""
                SELECT id FROM Users WHERE username = ?
                """,
                  (username,))
        rows = c.fetchall()
        for row in rows:
            print(f"BSDB Username_Available:  Found user")
            for key in rows[0].keys():
                print(f"{key}: {rows[0][key]}")
        available = (len(rows) == 0)
        return available

    def set_account_information(self, user_id, req):
        """
        Changes the user account information.
        Accepts:
            user_id (int): user id number
            req (JSON): body of request from user
        Returns:
            True if successful change, false if not
        """
        c = self.db.cursor()
        try:
            c.execute("""
                    UPDATE Users
                    SET 
                        username = ?,
                        email = ?,
                        fName = ?,
                        lName = ?,
                        streetAddress = ?,
                        city = ?,
                        state = ?,
                        postCode = ?
                    WHERE
                        id = ?
                    """,
                      (
                          req['username'],
                          req['email'],
                          req['fName'],
                          req['lName'],
                          req['streetAddress'],
                          req['city'],
                          req['state'],
                          req['postCode'],
                          user_id
                      )
                      )
            self.db.commit()
        except sqlite3.Error as e:
            print(e)
            raise Exception

    def get_password(self, user_num):
        """
        Checks if the password is correct.
        Accepts:
            user_num (int): User id of logged in user
        Returns:
            user's password
        """
        c = self.db.cursor()
        try:
            c.execute("SELECT password FROM Users WHERE id = ?",
                      (user_num,))
            results = c.fetchone()
            return results[0]
        except sqlite3.Error as e:
            print(e)
            raise Exception

    def set_password(self, user_num, password):
        """
        Changes the user password.
        Accepts:
            user_num (int): Logged in user ID number in Users table
            password (string): new password
        Returns:
            None
        """
        c = self.db.cursor()
        try:
            c.execute("UPDATE Users SET password = ? WHERE id = ?",
                      (password, user_num))
            self.db.commit()
            return
        except sqlite3.Error as e:
            print(e)
            raise Exception

    def get_recent_additions(self, num):
        """
        Returns the most recent available additions to the site.
        Accepts:
            num (int): Number of recent additions to be returned
        Returns:
            Array of Row objects
        """
        c = self.db.cursor()
        try:
            c.execute("""SELECT
                    title,
                    author,
                    ISBN,
                    externalLink,
                    CopyQualities.qualityDescription AS copyQuality,
                    Users.username AS listingUser,
                    UserBooks.id AS userBooksId,
                    CAST ((julianday('now') - julianday(UserBooks.dateCreated)) AS INTEGER) AS timeHere,
                    UserBooks.points as pointsNeeded
                    FROM Books 
                    INNER JOIN UserBooks 
                        on Books.id = UserBooks.bookId
                    INNER JOIN CopyQualities 
                        on UserBooks.copyQualityId = CopyQualities.id
                    INNER JOIN Users
                        on UserBooks.userId = Users.id
                    WHERE UserBooks.available == 1
                    ORDER BY
                    UserBooks.dateCreated DESC
                    LIMIT ?""",
                      (num,))
            recent_books = c.fetchall()
            print(recent_books)
            return recent_books
        except sqlite3.Error as e:
            print(e)
            return {}

    def get_books_by_ISBN(self, ISBN):
        """
        Checks UserBooks table for all books with ISBN.
        Accepts:
            ISBN (string): ISBN search criteria
        Returns:
            Array of Row objects
        """
        print(f"BSDB: Fetching local ISBN matches for {ISBN}")
        c = self.db.cursor()
        try:
            c.execute("""SELECT
                    title,
                    author,
                    ISBN,
                    externalLink,
                    Users.username as listingUser,
                    CopyQualities.qualityDescription as copyQuality,
                    CAST ((julianday('now') - julianday(UserBooks.dateCreated)) AS INTEGER) AS timeHere,
                    UserBooks.points as pointsNeeded,
                    UserBooks.id as UserBooksId
                    FROM Books
                    INNER JOIN UserBooks
                        on Books.id = UserBooks.bookId
                    INNER JOIN CopyQualities
                        on UserBooks.copyQualityId = CopyQualities.id
                    INNER JOIN Users
                        on UserBooks.userId = Users.id
                    WHERE
                        ISBN = ?
                    ORDER BY
                        UserBooks.dateCreated
                        """,
                      (ISBN,))
            isbn_match = c.fetchall()
            print("BSDB: Get_Books_By_ISBN (local) Results")
            self.print_results(isbn_match)
            return isbn_match
        except sqlite3.Error as e:
            print(e)
            return {}

    def get_books_by_author_and_title(self, author, title):
        """
        Checks Books table for books with both author and title match.
        Accepts:
            author (string): author search criteria
            title (string): title search criteria
        Returns:
            Array of Row objects
        """
        print(f"BSDB: Fetching local author and title matches for {author} and {title}")
        c = self.db.cursor()
        if len(author) == 0 or len(title) == 0:
            return {}
        try:
            c.execute("""SELECT
                    title,
                    author,
                    ISBN,
                    externalLink,
                    Users.username as listingUser,
                    CopyQualities.qualityDescription as copyQuality,
                    CAST ((julianday('now') - julianday(UserBooks.dateCreated)) AS INTEGER) AS timeHere,
                    UserBooks.points as pointsNeeded,
                    UserBooks.id as UserBooksId
                    FROM Books
                    INNER JOIN UserBooks
                        on Books.id = UserBooks.bookId
                    INNER JOIN CopyQualities
                        on UserBooks.copyQualityId = CopyQualities.id
                    INNER JOIN Users
                        on UserBooks.userId = Users.id
                    WHERE
                        author LIKE '%'||?||'%'
                    AND
                        title LIKE '%'||?||'%'
                    ORDER BY
                        author = ? DESC,
                        title = ? DESC,
                        author LIKE ?||'%' DESC,
                        author LIKE '%'||? DESC,
                        author
                        """,
                      (author, title, author, title, author, author))
            author_and_title_match = c.fetchall()
            print("BSDB: get_books_by_author_and_title (local) Results")
            self.print_results(author_and_title_match)
            return author_and_title_match
        except sqlite3.Error as e:
            print(e)
            return {}

    def get_books_by_author_or_title(self, author, title):
        """
        Checks Books table for books with author or title match.
        Accepts:
            author (string): author search criteria
            title (string): title search criteria
        Returns:
            Array of Row objects
        """
        print(f"BSDB: Fetching local author or title matches for {author} and {title}")
        if len(author) == len(title) == 0:
            return {}
        query_start = """
            SELECT 
                title, 
                author, 
                ISBN, 
                externalLink,
                Users.username as listingUser,
                CopyQualities.qualityDescription as copyQuality,
                CAST 
                    ((julianday('now') - julianday(UserBooks.dateCreated)) 
                        AS INTEGER) AS timeHere,
                UserBooks.points as pointsNeeded,
                UserBooks.id as UserBooksId
            FROM Books
            INNER JOIN UserBooks
                on Books.id = UserBooks.bookId
            INNER JOIN CopyQualities
                on UserBooks.copyQualityId = CopyQualities.id
            INNER JOIN Users
                on UserBooks.userId = Users.id
            """
        query_middle = " WHERE "
        query_end = " ORDER BY "
        params = []
        author_exists = title_exists = False
        if len(author) > 0:
            author_exists = True
        if len(title) > 0:
            title_exists = True
        if author_exists:
            query_middle += "author LIKE '%'||?||'%' "
            params.append(author)
            if title_exists:
                query_middle += " OR "
        if title_exists:
            query_middle += "title LIKE '%'||?||'%'"
            query_end += " title = ? DESC,"
            params += [title, title]
        if author_exists:
            query_end += " author = ? DESC,"
            params.append(author)
        if title_exists:
            query_end += " title LIKE ?||'%' DESC,"
            params.append(title)
        if author_exists:
            query_end += " author LIKE ?||'%' DESC,"
            params.append(author)
        if title_exists:
            query_end += " title LIKE '%'||? DESC,"
            params.append(title)
        if author_exists:
            query_end += " author LIKE '%'||? DESC,"
            params.append(author)
        query_end += " author"
        query = query_start + query_middle + query_end
        params = tuple(params)
        # print("\t Query:")
        # print(f"\t\t {query}")
        # print(f"\t\t {params}")
        c = self.db.cursor()
        try:
            c.execute(query, params)
            author_or_title_match = c.fetchall()
            print("BSDB: get_books_by_author_or_title (local) Results")
            self.print_results(author_or_title_match)
            return author_or_title_match
        except sqlite3.Error as e:
            print(e)
            return {}

    def print_results(self, rows):
        """
        Prints results.
        Accepts:
            rows (Row objects): returns from SQL query
        Returns:
            None
        """
        print("Printing Search Results:")
        i = 1
        for row in rows:
            print(f"\t Result #{i}:")
            for key in row.keys():
                print(f"\t\t {key}: {row[key]}")
            i += 1
        return

    def get_wishlists_by_userid(self, user_id):
        c = self.db.cursor()
        c.execute("SELECT id, userId, dateCreated FROM Wishlists WHERE userId = ?",
                  (session["user_num"],))
        return c.fetchall()

    def get_book_details_for_wishlists(self, wishlist_ids):
        """
        wishlist_ids is a list of Wishlists.id values
        Returns a list of Rows, each one corresponding to a book in a given wishlist, with
        the keys: 'wishlistId', 'bookTitle', 'dateCreated'
        """
        c = self.db.cursor()
        values = ""
        for id in wishlist_ids:
            values += str(id) + ', '
        values = values[:-2]
        c.execute(
            "SELECT wishlistId, Books.title bookTitle, dateCreated FROM WishlistsBooks w INNER JOIN Books ON w.bookId "
            "= Books.id WHERE "
            "wishlistId IN (?)",
            (values,))
        return c.fetchall()


def get_bsdb() -> BookSwapDatabase:
    return BookSwapDatabase()

# @app.teardown_appcontext
# def close_connection(exception):
# """
# When we teardown the app, we must close the database file.
# ""
# db = getattr(g, '_database', None)
# if db is not None:
# db.close()
# """
