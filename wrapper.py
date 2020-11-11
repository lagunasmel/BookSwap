from functools import wraps
from flask import session, redirect, url_for


# pass no argument to hide routes from users that aren't logged in
# a valid argument might be something like "admin", giving access to certain pages only to administrators
def login_required(status=None):
    def login_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' in session and (status is None or status in session):
                return func(*args, **kwargs)
            else:
                return redirect(url_for('login'))
        return wrapper
    return login_decorator
