import sqlite3
from flask import g

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
        if len(rows) != 1:
            raise KeyError("User ID did not return one row (could be none, could be multiple)")
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
                    SELECT B.title AS Title, B.ISBN AS ISBN, B.author AS Author, CQ.qualityDescription AS Quality,
                    UB.id AS id FROM UserBooks UB INNER JOIN Books B on UB.bookId = B.id 
                    INNER JOIN CopyQualities CQ ON UB.copyQualityId = CQ.id 
                    WHERE userId = ?""", (user_num,))
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


    def user_add_book_by_isbn(self, isbn, user_num, copyquality):
        """
        'user_id' user lists the book matching 'isbn' as available to swap.
        Nothing happens on failure.

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
        c.execute("""INSERT INTO UserBooks (userId, bookId, copyQualityId) VALUES (?, ?, ?)""", (user_num, book_id, copyquality))

    def username_available(self, username):
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
                (username, ))
        rows = c.fetchall()
        for row in rows:
            print(f"BSDB Username_Available:  Found user")
            for key in rows[0].keys():
                print(f"{key}: {rows[0][key]}")
        available = (len(rows) == 0)
        return available

    def change_account_information(self, user_id, req):
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
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def check_password(self, user_num, old_password):
        """
        Checks if the password is correct.
        Accepts:
            user_num (int): User id of logged in user
            old_password (string): User-entered old password
        Returns:
            True if old_password is correct, false if it is not
        """
        c = self.db.cursor()
        try:
            c.execute("SELECT password FROM Users WHERE id = ?",
                    (user_num, ))
            results = c.fetchone()
            return old_password == results[0]
        except sqlite3.Error as e:
            print(e)
            return

    def change_password(self, user_num, req):
        """
        Changes the user password.
        Accepts:
            user_num (int): Logged in user ID number in Users table
            req (JSON): body of request from user
        Returns:
            True if successful chnage, false if not
        """
        c = self.db.cursor()
        try:
            c.execute("UPDATE Users SET password = ? WHERE id = ?;",
                    ( req['newPassword'], user_num))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(e)
            return False


# @app.teardown_appcontext
# def close_connection(exception):
# """
# When we teardown the app, we must close the database file.
# ""
# db = getattr(g, '_database', None)
# if db is not None:
# db.close()
# """
