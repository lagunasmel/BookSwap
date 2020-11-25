from db_connector import get_db, BookSwapDatabase
import logging

log = logging.getLogger('app.sub')

class Wishlists:
    """
    Wishlists contains the structure and methods for populating a user's
        `my-wishlists` route.
    """

    def __init__(self, user_num, bsdb):
        """
        Class initializer.  Opens database object for use, and set's 
            user's id number.
        Accepts:
            user_num (int): Users.id
            bsdb (BookSwapDatabase instance): database access object
        """
        self.user_num = user_num
        self.bsdb = bsdb

    def get_all_wishlist_books_for_user(self):
        """
        Get_all_wishlist_books_for_user returns an array of dictionaries, each representing a Book entry.
        Accepts:
            None
        Returns:
            List of dicts.  Each dict is a book in a user's wishlist.
        """
        try:
            wishlists = self._get_all_wishlists_for_user()
            books = self._get_books_for_wishlists(wishlists)
            log.info(f"Created books in wishlist for user {self.user_num}")
        except Exception:
            log.error(f"Error retrieving book details for wishlists for user {self.user_num}")
            raise Exception
        return books


    def _get_all_wishlists_for_user(self):
        """
        _Get_all_wishlists_for_user returns a list of wishlist ids belonging 
            to that user.
        Accepts:
            None
        Returns:
            List of ints
        """
        try:
            wishlist_rows = self.bsdb.get_wishlists_by_userid(self.user_num)
        except Exception:
            log.error(f"Error getting wishlists for user {self.user_num}")
            raise Exception
        wishlists = [row['id'] for row in wishlist_rows]
        return wishlists


    def _get_books_for_wishlists(self, wishlists):
        """
        _Get_books_for_wishlists gives a list of dictionaries, each
            representing a book in the user's wishlist.
        Accepts:
            wishlists (list of ints): List of Wishlists.id
        Returns:
            List of dictionaries
        """
        books = []
        for wishlist in wishlists:
            try:
                books += self.bsdb.get_book_details_for_wishlist(wishlist)
            except Exception:
                log.error(f"Error getting books for wishlist {wishlist}")
                raise Exception
        books = [dict(book) for book in books]
        return books

       
