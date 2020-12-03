import sys
import sqlite3
from book_search import BookSearch
from wishlists import Wishlists
from my_requests import MyRequests
from account import AccountSettings
from cancel_request import CancelTradeRequest
from book_received import BookReceived
from flask import Flask, render_template, url_for, flash, redirect, session, g, json
from flask import request as req
from db_connector import get_db, BookSwapDatabase, get_bsdb
from forms import (RegistrationForm, LoginForm, BookSearchForm,
                   AccountSettingsChangeForm, PasswordChangeForm)
from auth import login_required, guest_required
import logging

app = Flask(__name__)

# Secret Key for Flask Forms security
app.config['SECRET_KEY'] = '31c46d586e5489fa9fbc65c9d8fd21ed'


# Code automatically created with each request
@app.before_request
def populate_g():
    bsdb = get_bsdb()
    user_num = session.get("user_num")
    if user_num is not None:
        try:
            user_info = bsdb.get_account_settings(user_num)
            g.username = user_info["username"]
            g.points = user_info["points"]
            g.num_trade_requests = bsdb.get_num_trade_requests(user_num)
            g.num_open_trades = bsdb.get_num_open_trades(user_num)
            app.logger.info(f"Request made.  Current user status:"
                            f"\t g.username: {g.username}" +
                            f"\t g.points: {g.points}"
                            f"\t g.num_trade_requests: {g.num_trade_requests}" +
                            f"\t g.num_open_trades: {g.num_open_trades}")


        except Exception:
            app.logger.error(f"Error setting up g")
            session['user_num'] = None


# Auto-closes db connection at the end of each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Landing Page
@app.route('/')
@app.route('/home')
@app.route('/index')
def home():
    return render_template('home.html')


# error handler for 500
@app.errorhandler(500)
def error_five_hundred(e):
    return render_template('500.html'), 500


# error handler for 404
@app.errorhandler(404)
def error_four_oh_four(e):
    return render_template('404.html'), 404


@app.route('/learn-how')
def learn_how():
    return render_template('learn-how.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/book-not-received/<user_books_id>')
@login_required
def book_not_received(user_books_id):
    app.logger.info(f"Incoming book NOT received confirmation from {session['user_num']} for book {user_books_id}")
    bsdb = get_bsdb()
    book_not_received = BookReceived(session['user_num'], user_books_id, bsdb)
    try:
        book_not_received.book_not_received()
        app.logger.info(f"Trade failure confirmation from user {session['user_num']} for book {user_books_id}")
        flash("Trade marked as never completed", "success")
    except Exception:
        app.logger.error(
            f"Unsuccessful trade failure confirmation from user {session['user_num']} for book {user_books_id}")
    return redirect(url_for("my_requests"))


@app.route('/book-received/<user_books_id>')
@login_required
def book_received(user_books_id):
    app.logger.info(f"Incoming book received confirmation from {session['user_num']} for book {user_books_id}")
    bsdb = get_bsdb()
    book_received = BookReceived(session['user_num'], user_books_id, bsdb)
    try:
        book_received.book_received()
        app.logger.info(
            f"Successful trade completion confirmation from user {session['user_num']} for book {user_books_id}")
        flash("Trade marked as completed", "success")
    except Exception:
        app.logger.error(
            f"Unsuccessful trade request confirmation from user {session['user_num']} for book {user_books_id}")
    return redirect(url_for("my_requests"))


@app.route('/cancel-request/<user_books_id>')
@login_required
def cancel_request(user_books_id):
    app.logger.info(f"Incoming trade request cancellation from {session['user_num']} for book {user_books_id}")
    bsdb = get_bsdb()
    cancel_trade_request = CancelTradeRequest(session['user_num'], user_books_id, bsdb)
    try:
        cancel_trade_request.cancel_request()
        app.logger.info(
            f"Successful trade request cancellation from user {session['user_num']} for book {user_books_id}")
        flash("Trade request canceled", "success")
    except Exception:
        app.logger.error(
            f"Unsuccessful trade request cancellation from user {session['user_num']} for book {user_books_id}")
    return redirect(url_for("my_requests"))


@app.route('/request-book', methods=['GET', 'POST'])
def requestBook():
    bsdb = get_bsdb()
    book = req.get_json(force=True)
    app.logger.info('Request incoming for book: %s', book)
    if (book['userId'] == session['user_num']):
        flash("You tried to request your own book?  It would be easier to just pull it off the shelf and read...",
              "warning")
        app.logger.warning(
            f"User {session['user_num']} attempted to trade with themselves.  This leads to night blindness")
        success = "False"
        try:
            points_available = bsdb.get_current_user_points(session["user_num"])
        except Exception:
            points_available = 0
    else:
        try:
            points_available = bsdb.request_book(book, session['user_num'])
            success = "True"
            app.logger.info(
                f"Successfully placed trade request for user {session['user_num']} on UserBooks number "
                f"{book['userBooksId']}")
        except Exception:
            app.logger.error(
                f"Unable to place the Trade Request for user {session['user_num']} on UserBooks book number "
                f"{book['userBooksId']}")
            success = "False"
            flash("There was an error in placing the trade request.  Feel free to try again", "warning")
    return {
        "book": book,
        "points_available": points_available,
        "success": success
    }


@app.route('/browse-books', methods=['GET', 'POST'])
def browse_books():
    form = BookSearchForm()
    bsdb = get_bsdb()
    recent_books = bsdb.get_recent_additions(8)
    recent_books_arr = [dict(book) for book in recent_books]
    local_results = {}
    external_results = {}
    if req.method == 'POST':
        book_search_query = (form.ISBN.data, form.author.data, form.title.data)
        book_search = BookSearch(book_search_query, bsdb)
        # TODO magic numbers here
        # book_results = book_search.local_book_search(10)
        local_results, external_results = book_search.combined_book_search(10, 10)
        show_recent = False
        show_search = False
        show_results = True
    else:
        book_results = {}
        show_recent = True
        show_search = True
        show_results = False

    # Load current user's points
    if session.get('user_num'):
        try:
            points_available = bsdb.get_current_user_points(session['user_num'])
            app.logger.info(f"User {session['user_num']} has {points_available} points.")
        except Exception:
            app.logger.error(
                f"APP: Browse_books -- Could not determine number of points for user {session['user_num']}.")
            points_available = 0
            flash(
                "We could not load your points, so we assume you have 0 points. Feel free to browse for now, "
                "but we will need to fix this before you can make trade requests.",
                "warning")
    else:
        points_available = 0

    app.logger.info(f"\n\t recent_books: {recent_books_arr}" +
                    f"\t local_results: {local_results}" +
                    f"\t external_results: {external_results}" +
                    f"\t form: {form}" +
                    f"\t Visiting user has {points_available} points available.")
    return render_template('browse-books.html',
                           recent_books=recent_books_arr,
                           local_results=local_results,
                           external_results=external_results,
                           form=form,
                           show_recent=show_recent,
                           show_search=show_search,
                           show_results=show_results,
                           points_available=points_available
                           )


@app.route('/change-points', methods=['GET', 'POST'])
@login_required
def change_points():
    """
    Change_points changes the point value assigned to the UserBooks entry.
    """
    bsdb = get_bsdb()
    points = req.get_json().get('points')
    user_num = session['user_num']
    book_id = req.get_json().get('id')
    app.logger.info(
        f"UserBooks id {book_id} trying to change it to {points} points. " +
        f"Current user is {session['user_num']}")
    # Confirm that the requesting user owns the book
    try:
        if bsdb.is_user_book_owner(user_num, book_id):
            app.logger.info(f"Correct user for the book detected.")
        else:
            app.logger.warning(f"Incorrect user for the book detected.")
            flash("Wrong uesr for that book.  Log out, log in, and try again?",
                  "warning")
            return redirect(url_for('my_books'))
    except Exception:
        app.logger.error("Error checking user validity.")
        flash("We had an error trying to verify your identity. " +
              "Sorry about that.  Perhaps try again?", "warning")
        return redirect(url_for('my_books'))
    # Change the points
    try:
        bsdb.set_book_points(book_id, points)
        app.logger.info(f"Book points changed.")
        flash("Book points successfully changed.", "success")
    except Exception:
        app.logger.error(f"Error changing book points.")
        flash("We had an error trying to change your book points. " +
              "Sorry about that.  Perhaps try again?", "warning")
    return redirect(url_for('my_books'))


@app.route('/received-requests')
@login_required
def received_requests():
    bsdb = get_bsdb()
    user = session['user_num']
    num_trade_reqs = bsdb.get_num_trade_requests(user)
    num_open_trades = bsdb.get_num_open_trades(user)
    if num_trade_reqs == 0 and num_open_trades == 0:
        return render_template('user/no-trades.html')
    else:
        trade_info = bsdb.get_trade_info(user)
        trade_info_dicts = [dict(row) for row in trade_info]
        return render_template('user/received-requests.html',
                               trade_info=trade_info_dicts,
                               num_open_trades=num_open_trades,
                               num_trade_reqs=num_trade_reqs)


@app.route('/my-requests')
@login_required
def my_requests():
    bsdb = get_bsdb()
    user = session['user_num']
    my_request = MyRequests(user, bsdb)
    try:
        requests = my_request.get_all_open_requests()
        requests_dicts = [dict(row) for row in requests]
        for trade in requests_dicts:
            print(trade['tradeAge'])
    except Exception:
        app.logger.error("Couldn't fill my-requests")
        requests_dicts = []

    if len(requests_dicts) == 0:
        return render_template('user/no-trades.html', no_sent_requests=True)
    else:
        return render_template('user/my-requests.html', requests=requests_dicts)


@app.route('/accept-trade/<user_books_id>')
@login_required
def accept_trade(user_books_id):
    app.logger.info(f"Incoming trade acceptance from user {session['user_num']} for book {user_books_id}")
    bsdb = get_bsdb()
    try:
        bsdb.accept_trade(user_books_id)
        app.logger.info(f"Trade successfully accepted.")
        flash("Trade successfully accepted", "success")
    except Exception:
        app.logger.info(f"There was an error in accepting the trade.")
        flash("There was an error in accepting your trade", "warning")
    return redirect(url_for('received_requests'))


@app.route('/reject-trade/<user_books_id>')
@login_required
def reject_trade(user_books_id):
    app.logger.info(f"Incoming trade rejection from user {session['user_num']} for book {user_books_id}")
    bsdb = get_bsdb()
    try:
        bsdb.reject_trade(user_books_id)
        app.logger.info(f"Trade successfully rejected.  UserBooks number {user_books_id} is available again.")
        flash("Trade successfully removed", "success")
    except Exception:
        app.logger.error(f"There was an error in rejecting the trade.")
        flash("There was an error in deleting your trade", "warning")
    return redirect(url_for('received_requests'))


@app.route('/login', methods=['GET', 'POST'])
@guest_required
def login():
    form = LoginForm()
    # Checks if input is valid
    if form.validate_on_submit():
        bsdb = get_bsdb()
        username = form.username.data
        password = form.password.data
        error = None
        app.logger.info(f'Login attempt incoming for user {username}')
        id = None
        # Username check
        try:
            id = bsdb.get_username_id(username)
        except Exception:
            app.logger.error(f"Error checking username ( {username} ).")
            error = "We had an error checking your username.  Please try again."

        if id is None:
            app.logger.error(f"Login -- Incorrect username ( {username} ) entered.")
            error = "Incorrect username.  We do not have record of this username."
        # Password check
        else:
            try:
                if password != bsdb.get_password(id):
                    app.logger.warning(f"Incorrect password entered for {username}.")
                    error = "Incorrect password."
            except Exception:
                app.logger.error(f"Error checking password for {username}.")
                error = "We hada n error checking your password.  Please try again."
        # No errors, login proceeds
        if error is None:
            session.clear()
            session['user_num'] = id
            app.logger.info(f"User {username} successfully logged in.")
            return redirect(url_for('home'))
        flash(error, 'warning')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
@guest_required
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        db = get_db()
        # db.row_factory = sqlite3.Row
        c = db.cursor()
        error = None
        # (Redundant) check for uesrname and password entries
        if not form.username.data:
            error = "Username is required."
        elif not form.password.data:
            error = "Password is required."
        elif c.execute('SELECT id FROM Users WHERE username = ?',
                       (form.username.data,)).fetchone() is not None:
            error = 'User {} already exists.  Please try again with a different username, or log in.'.format(
                form.username.data)
        elif c.execute('SELECT id FROM Users WHERE email = ?',
                       (form.email.data,)).fetchone() is not None:
            error = 'User with email {} already exists. Please try again with a different email, or log in.'.format(
                form.email.data)
        if error is None:
            c.execute("""INSERT INTO Users (
            'username', 
            'password', 
            'email', 
            'fName', 
            'lName', 
            'streetAddress', 
            'city', 
            'state', 
            'postCode') 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (form.username.data,
                       form.password.data,
                       form.email.data,
                       form.fName.data,
                       form.lName.data,
                       form.streetAddress.data,
                       form.city.data,
                       form.state.data,
                       form.postCode.data))
            app.logger.info(
                f"Signup: account created for {form.username.data}, " +
                f"with User id {c.lastrowid}")
            flash(f'Account created for {form.email.data}!', 'success')
            session['user_num'] = c.lastrowid

            c.execute("INSERT INTO Wishlists (userId) VALUES (?)", (c.lastrowid,))  # Default wishlist for user
            db.commit()

            return redirect(url_for('account'))
        flash(error, 'warning')
    return render_template('signup.html', form=form)


@app.route('/wishlist', methods=['GET', 'POST'])
@login_required
def wishlist():
    bsdb = get_bsdb()
    wishlists = Wishlists(session['user_num'], bsdb)
    data = req.get_json()
    # User asks to see copies of a book
    if req.method == "POST" and data.get("request") == "copiesModal":
        book = eval(data['book'])
        app.logger.info(f"Request incoming for copies of book {book} from user {session['user_num']}")
        try:
            copies = bsdb.get_available_copies(book["bookId"], session["user_num"])
            copies_arr = [dict(copy) for copy in copies]
            app.logger.info(f"Copies available: {copies_arr}")
        except Exception:
            app.logger.error(f"Error retrieving copies of {book} for user {session['user_num']}")
            flash("Error retrieving copies of the book.  Maybe try again?", "warning")
            return redirect('/wishlist')
        return {
            "title": copies_arr[0]['title'],
            "copies": copies_arr,
            "count": len(copies_arr),
            "points_available": g.points
        }
    # Page load
    try:
        books = wishlists.get_all_wishlist_books_for_user()
        app.logger.info(f"Made wishlists for user {session['user_num']}")
    except Exception:
        app.logger.error(f"Error making wishlists for user {session['user_num']}")
        flash("We had an error fetching your wishlist", "warning")
        books = []
    return render_template('user/wishlist.html', books=books)


@app.route('/add-to-wishlist/<bookid>', methods=['GET'])
@app.route('/add-to-wishlist', methods=['GET'])
@login_required
def add_to_wish(bookid=None):
    bsdb = get_bsdb()
    db = get_db()
    db.row_factory = sqlite3.Row

    # Queries used for SELECTing and INSERTing
    get_books_isbn_query = 'SELECT * FROM Books WHERE ISBN = ?'
    get_wishlist_books_query = 'SELECT * FROM WishlistsBooks WHERE wishlistId = ? AND bookId = ?'
    insert_wishlist_query = 'INSERT INTO WishlistsBooks (wishlistId, bookId) VALUES (?, ?)'

    # Special path for browse-books route
    if bookid is not None:
        c = db.cursor()
        c.execute(get_wishlist_books_query,
                  (session['user_num'], bookid))

        # if the book was already in the wishlist, don't add it
        if c.fetchall():
            flash("Book already in your wishlist", "warning")
            app.logger.warning(f"Book {bookid} already in " +
                               f"user {session['user_num']}'s wishlist")
        # otherwise, add book to the wishlist
        else:
            c.execute(insert_wishlist_query,
                      (session['user_num'], bookid))
            flash("Book added to your wishlist", "success")
            app.logger.info(f"Book {id} successfully added to " +
                            f"user {session['user_num']}'s wishlist")
        db.commit()
        db.close()
        return redirect(url_for('browse_books'))
    data = req.args.get("isbn")
    if data == "":
        return redirect('/wishlist')
    c = db.cursor()
    c.execute(get_books_isbn_query, (data,))
    bookId = c.fetchall()[0]['id']
    # need to get Users Wishlist.id number
    c.execute("""
                SELECT
                    id
                FROM 
                    Wishlists
                WHERE
                    Wishlists.userId = ?
                """,
              (session['user_num'],))
    wishlist = c.fetchone()['id']
    c.execute(get_wishlist_books_query,
              (wishlist, bookId))
    if not c.fetchall():
        flash("Book successfully added to your wishlist", "success")
        app.logger.info(f"Book {bookId} added to wishlist {wishlist}")
        c.execute(insert_wishlist_query,
                  (wishlist, bookId))
    else:
        flash("Book already in your wishlist.", "warning")
        app.logger.warning(f"Book {bookId} attempted to add to wishlist {wishlist}, but it was already in that list.")
    db.commit()
    db.close()
    return redirect('/wishlist')


@app.route('/remove-from-wishlist', methods=['GET'])
@login_required
def remove_wish():
    db = get_db()
    db.row_factory = sqlite3.Row

    c = db.cursor()

    wishID = req.args.get("wishlistRem")
    bookID = req.args.get("bookRem")
    app.logger.info(f"Removing book {bookID} from wishlist {wishID} for " +
                    f" user [session['user_num']")
    c.execute("DELETE FROM WishlistsBooks WHERE wishlistId = ? AND bookId = (SELECT id FROM Books WHERE title = ?)",
              (wishID, bookID))
    db.commit()
    db.close()

    return redirect('/wishlist')


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    # Get basic database and forms ready to return
    bsdb = get_bsdb()
    acct = AccountSettings(session['user_num'])
    account_settings_change_form = AccountSettingsChangeForm()
    password_change_form = PasswordChangeForm()
    account_settings = bsdb.get_account_settings(session["user_num"])
    show_account_modal = False
    show_password_modal = False
    # Check against requests to change account settings
    if (req.method == 'POST' and
            account_settings_change_form.submit_account_change.data):
        show_account_modal = True
        app.logger.info(f"request received to change user settings for " +
                        f"user {session['user_num']}")
        # Check to make sure form was valid, return form if it was not
        if not account_settings_change_form.validate_on_submit():
            app.logger.warning(f"Settings change form failed validation")
            flash("Your information wouldn't work.  Try again?", "warning")
            return render_template(
                'user/user-home.html',
                account_settings=account_settings,
                account_settings_change_form=account_settings_change_form,
                password_change_form=password_change_form,
                show_account_modal=show_account_modal,
                show_password_modal=show_password_modal
            )
        # Check that the username isn't changing or is available
        if acct.is_username_valid(session['user_num'],
                                  account_settings_change_form.username.data):
            app.logger.info("username is valid")
            try:
                acct.set_account_information(
                    session['user_num'], account_settings_change_form)
                flash("Account information updated.", "success")
                app.logger.info("returning new account info:")
                account_settings = bsdb.get_account_settings(
                    session["user_num"])
                show_account_modal = False
                account_settings = bsdb.get_account_settings(
                    session["user_num"])
            except Exception:
                flash("Error updating your information.  Try again?",
                      "warning")
        else:
            flash("Username is already taken", "warning")

    # Check against request to change password
    elif req.method == 'POST' and password_change_form.submit.data:
        show_password_modal = True
        app.logger.info(f"request received to change password for " +
                        f"user {session['user_num']}")
        if not password_change_form.validate_on_submit():
            app.logger.warning(f"Password change form failed verification")
            flash("Your infromation wouldn't work.  Try again?", "warning")
            return render_template(
                'user/user-home.html',
                account_settings=account_settings,
                account_settings_change_form=account_settings_change_form,
                password_change_form=password_change_form,
                show_account_modal=show_account_modal,
                show_password_modal=show_password_modal
            )
        try:
            correct_password = acct.is_password_correct(session["user_num"],
                                                        password_change_form)
            if not correct_password:
                flash("Original password was not correct.  Please try again.",
                      "warning")
            else:
                app.logger.info("Original password was entered correctly.")
                try:
                    acct.set_password(session["user_num"],
                                      password_change_form)
                    app.logger.info("New Password set")
                    flash("New Password Sucessfully Set.", "success")
                    show_password_modal = False
                except Exception:
                    app.logger.error("Error setting new password")
                    flash("Error setting new password.  Try again?", "warning")

        except Exception:
            flash("Error determining if the original password is correct.  Try again?", "warning")
            app.logger.error("Error checking original password.")

    # We got here either by being GET or succeeding making changes.
    # Refill account_setting and account_settings_change_form
    account_settings_change_form = acct.fill_account_settings_change_form()
    account_settings = bsdb.get_account_settings(session["user_num"])
    return render_template(
        'user/user-home.html',
        account_settings=account_settings,
        account_settings_change_form=account_settings_change_form,
        password_change_form=password_change_form,
        show_account_modal=show_account_modal,
        show_password_modal=show_password_modal
    )


@app.route('/_add-book', methods=['POST'])
@login_required
def add_book():
    """
    This method lists a book on one of several lists, by a user. It involves the following steps:
    - add the book to the backend DB to the relevant table
    - then, reload the page with an updated table
    """
    bsdb = get_bsdb()
    data = req.get_json()
    if data.get('request') == 'my-books':  # here we list the book as being available for trade
        # isbn = req.get_json()["isbn"]
        copyquality = data["quality"]
        points = data["points"]
        book_id = data["bookId"]
        user_num = session["user_num"]
        # bsdb.user_add_book_by_isbn(isbn, user_num, copyquality)
        bsdb.user_add_book_by_id(book_id, user_num, copyquality, points)
        app.logger.info(f"Book {book_id} added by user {user_num}")
        flash("Book successfully added to your BookSwap library.", "success")

        return redirect('/my-books')
    elif data.get('request') == 'my-wishlist':
        book_id = data["bookId"]
        user_num = session["user_num"]
        bsdb.user_add_book_to_wishlist_by_id(book_id, user_num)
        return redirect('/wishlist')


@app.route('/_search-book', methods=['POST'])
@login_required
def search_book():
    """
    This method is POSTed a request with the fields 'isbn', 'author', and 'title', and searches for
    results on the open library API that match these fields. It returns a rendered set of divs to be inserted
    into the html as appropriate.
    """
    bsdb = get_bsdb()
    data = req.get_json()
    if data.get('request') == 'my-books':
        isbn = data["isbn"]
        author = data["author"]
        title = data["title"]
        # TODO magic number here - number of search results
        search_results = bsdb.search_books_openlibrary(title=title, author=author, isbn=isbn, num_results=5)
        copyqualities = bsdb.get_book_qualities()
        return render_template("snippets/external_search_results.html", search_results=search_results,
                               copyqualities=copyqualities, show_qualities=True, show_points=True)
    elif data.get('request') == 'my-wishlist':
        isbn = data["isbn"]
        author = data["author"]
        title = data["title"]
        # TODO magic number here - number of search results
        search_results = bsdb.search_books_openlibrary(title=title, author=author, isbn=isbn, num_results=5)
        return render_template("snippets/external_search_results.html", search_results=search_results,
                               show_qualities=False, show_points=False, show_wishlist_results=True)


@app.route('/remove-from-user-library', methods=['GET'])
@login_required
def remove_book():
    db = get_db()
    db.row_factory = sqlite3.Row

    c = db.cursor()

    bookID = req.args.get("bookRem")
    c.execute("DELETE FROM UserBooks WHERE id = ?",
              (bookID,))
    new_points = c.execute("SELECT points FROM Users WHERE id = (?)", (session['user_num'],)).fetchone()['points'] - 0.1
    c.execute("""UPDATE Users SET points = (?) WHERE id = (?)""", (new_points, session['user_num']))
    db.commit()
    db.close()
    app.logger.info(f"Book {bookID} removed from user {session['user_num']}")
    flash("Book removed from your BookSwap library.", "success")
    return redirect('/my-books')


@app.route('/my-books')
@login_required
def my_books():
    bsdb = get_bsdb()
    # Get the data of books currently listed
    rows = bsdb.get_listed_books(session['user_num'])
    copyqualities = bsdb.get_book_qualities()
    # Build the data to be passed to Jinja
    headers = ["Title", "Author", "Quality", "Points", "ISBN", "ID", "Cover"]
    table_content = [[row[header] for header in headers] for row in rows]
    data = {"headers": headers,
            "rows": table_content,
            "caption": "",
            "copyqualities": copyqualities
            }
    return render_template('user/my-books.html', data=data)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/reset-db')
def reset_db():
    """
    A "secret" route for resetting database specs and content.
    """
    with app.app_context():
        db = get_db()
        with app.open_resource('DatabaseSpecs/database-definition-queries.sql',
                               mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    return "Database reset :)"


if __name__ == '__main__':
    """
    `host` keyword arg added by Ben to make it work on his server.  It seems to 
    work the same on his local machine.  Maybe others can test too?
    """
    app.run(host='0.0.0.0', debug=True)
