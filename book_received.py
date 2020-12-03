from db_connector import BookSwapDatabase
import logging

log = logging.getLogger('app.sub')

class BookReceived:
    """
    BookReceived contains the structure and methods for marking a traded book 
        as received
    """

    def __init__(self, user_num, user_books_id, bsdb):
        """
        Class initializer.  Opens database objuect for use and sets user's id
            number.
        Accepts:
                user_num (int): Users.id
                user_books_id (int): UserBooks.id
                bsdb (BookSwapDatabase instance): databse access object
        """
        self.user_num = user_num
        self.user_books_id = user_books_id
        self.bsdb = bsdb

    def book_received(self):
        """
        Book_received attempts to change a user's trade request to fulfilled,
            after performing some logic security checks.
        Accepts:
            Nothing
        Returns:
            True upon successful request, False upon a failed security check
                (user wrong user, book not in open request status), raises
                Exception for error.
        """
        # Confirm the book is in open trade status
        try:
            status = self.bsdb.get_trade_status(self.user_books_id)
        except Exception:
            log.error(f"Confirming trade status for UserBooks {self.user_books_id} on behalf of user {self.user_num}")
            flash("Error confirming trade status of the book", "warning")
        if status['statusId'] != 3:
            log.error(f"UserBooks entry {self.user_books_id} is not in accepted trade request state.")
            flash("Cannot confirm trade fulfillment for this book", "warning")
            return False
        # Confirm that this user is the book requester
        try:
            requester = self.bsdb.get_trade_requester(self.user_books_id)
        except Exception:
            log.error(f"Confirming User {self.user_books_id} as the trade requester")
            flash("Error confirming correct requesting user", "warning")
            raise Exception
        if requester['userRequestedId'] != self.user_num:
            log.error(f"Wrong requesting user.  Attempted by User {self.user_num} on trade on {self.user_books_id}")
            flash("Cannot confirm trade fulfillment for this book", "warning")
            return False
        # attempt actual completion
        try:
            self.bsdb.book_received_by_requester(self.user_books_id, self.user_num)
        except Exception:
            log.error(f"Performing trade fulfillment on  book {self.user_books_id} for user {self.user_num}")
            flash("We had an error completing the trade", "warning")
            raise Exception
        return True
    
    def book_not_received(self):
        """
        Book_not_received attempts to change a user's trade request to not 
            completed, after performing some logic security checks.
        Accepts:
            Nothing
        Returns:
            True upon successful request, False upon a failed security check
                (user wrong user, book not in open request status), raises
                Exception for error.
        """
        # Confirm the book is in open trade status
        try:
            status = self.bsdb.get_trade_status(self.user_books_id)
        except Exception:
            log.error(f"Confirming trade status for UserBooks {self.user_books_id} on behalf of user {self.user_num}")
            flash("Error confirming trade status of the book", "warning")
        if status['statusId'] != 3:
            log.error(f"UserBooks entry {self.user_books_id} is not in accepted trade request state.")
            flash("Cannot confirm trade failure for this book", "warning")
            return False
        # Confirm that this user is the book requester
        try:
            requester = self.bsdb.get_trade_requester(self.user_books_id)
        except Exception:
            log.error(f"Confirming User {self.user_books_id} as the trade requester")
            flash("Error confirming correct requesting user", "warning")
            raise Exception
        if requester['userRequestedId'] != self.user_num:
            log.error(f"Wrong requesting user.  Attempted by User {self.user_num} on trade on {self.user_books_id}")
            flash("Cannot confirm trade failure for this book", "warning")
            return False
        # Confirm that the trade is at least 4 weeks old
        try:
            trade = self.bsdb.get_trade_age(self.user_books_id)
        except Exception:
            log.error(f"Confirming that the trade is old enough")
            flash("Error confirming correct age of trade request", "warning")
            raise Exception
        if trade['tradeAge'] <= 28:
            log.error(f"Trade not old enough to qualify for marking as incomplete.  UserBooks {self.user_books_id} and user {self.user_num}")
            flash("Trade request is not old enough to be marked incomplete", "warning")
            return False
        # attempt actual trade marking as unfulfilled
        try:
            self.bsdb.book_not_received_by_requester(self.user_books_id, self.user_num)
        except Exception:
            log.error(f"Performing trade marking as not complete on  book {self.user_books_id} for user {self.user_num}")
            flash("We had an error marking the trade as incomplete", "warning")
            raise Exception
        return True




