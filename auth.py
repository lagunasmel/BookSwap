import functools

from flask import redirect, session, url_for


"""
Decorator for pages that require user be logged in.  Redirects
guest user to login page.
"""
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_num') is None:
            return redirect(url_for("login"))

        return view(**kwargs)

    return wrapped_view
    

"""
Decorator for pages that are only for guests.  Redirects logged in user
to `account settings` page.
"""
def guest_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_num') is not None:
            return redirect(url_for("account"))

        return view(**kwargs)

    return wrapped_view
