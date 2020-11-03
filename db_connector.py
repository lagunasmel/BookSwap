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

# @app.teardown_appcontext
# def close_connection(exception):
    # """
    # When we teardown the app, we must close the database file.
    # ""
    # db = getattr(g, '_database', None)
    # if db is not None:
        # db.close()
# """
