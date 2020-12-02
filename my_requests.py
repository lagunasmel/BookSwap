from db_connector import get_db, BookSwapDatabase
import logging

log = logging.getLogger('app.sub')

class MyRequests:
    """
    Requests contains the structure and methods for populating a user's 
    'my-requests' route.
    """

    def __init__(self, user_num, bsdb):
        """
        Class initializer. Opens database ojbect for use, and sets user's
            id number.
        Accepts:
            user_num (int): Users.id
            bsdb (BookSwapDatabase instance): database access object
        """
        self.user_num = user_num
        self.bsdb = bsdb

    def get_all_open_requests(self):
        try:
            requests = self.bsdb.get_all_open_requests(self.user_num)
        except Exception:
            log.error("Error getting open requests")
        return requests
