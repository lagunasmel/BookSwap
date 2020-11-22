import sqlite3
from book_search import BookSearch
from account import AccountSettings
from flask import Flask, render_template, url_for, flash, redirect, session, g, json
from flask import request as req
from db_connector import get_db, BookSwapDatabase, get_bsdb
from forms import (RegistrationForm, LoginForm, BookSearchForm,
                   AccountSettingsChangeForm, PasswordChangeForm)
from auth import login_required, guest_required

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
            print("APP: Before_request")
            g.username = user_info["username"]
            print(f"\t g.username: {g.username}")
            g.points = user_info["points"]
            print(f"\t g.points: {g.points}")
            g.num_trade_requests = bsdb.get_num_trade_requests(user_num)
            print(f"\t g.num_trade_requests: {g.num_trade_requests}")
            g.num_open_trades = bsdb.get_num_open_trades(user_num)
            print(f"\t g.num_open_trades: {g.num_open_trades}")

        except Exception:
            print(f"APP: App_context -- Error setting up g")
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


@app.route('/learn-how')
def learn_how():
    return render_template('learn-how.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/request-book', methods=['GET', 'POST'])
def requestBook():
    bsdb = get_bsdb()
    book = req.get_json(force=True)
    print(f"APP: RequestBook -- Request incoming for book:  {book}")
    if (book['userId'] == session['user_num']):
        flash("You tried to request your own book?  It would be easier to just pull it off the shelf and read...",
              "warning")
        print(f"APP: Request_Book: User attempted to trade with themselves.  This leads to night blindness")
        success = "False"
        try:
            points_available = bsdb.get_current_user_points(session["user_num"])
        except Exception:
            points_available = 0
    else:
        try:
            points_available = bsdb.request_book(book, session['user_num'])
            success = "True"
            print(
                f"APP: RequestBook -- Successfully placed trade request for user {session['user_num']} on UserBooks number {book['userBooksId']}")
        except Exception:
            print(
                f"APP: RequestBook -- Unable to place the Trade Request for user {session['user_num']} on UserBooks book number {book['userBooksId']}")
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
    recent_books_arr = []
    for i in range(len(recent_books)):
        recent_books_arr.append({key: recent_books[i][key] for key in recent_books[i].keys()})
    if req.method == 'POST':
        book_search_query = (form.ISBN.data, form.author.data, form.title.data)
        book_search = BookSearch(book_search_query, bsdb)
        book_results = book_search.local_book_search(10)
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
            print(f"APP: Browse_books -- User {session['user_num']} has {points_available} points.")
        except Exception:
            print(f"APP: Browse_books -- Could not determine number of points for user {session['user_num']}.")
            points_available = 0
            flash(
                "We could not load your points, so we assume you have 0 points. Feel free to browse for now, but we will need to fix this before you can make trade requests.",
                "warning")
    else:
        points_available = 0

    print("APP: Browse_books:")
    print(f"\t recent_books: {recent_books_arr}")
    print(f"\t book_results: {book_results}")
    print(f"\t form: {form}")
    print(f"\t Visiting user has {points_available} points available.")
    return render_template('browse-books.html',
                           recent_books=recent_books_arr,
                           book_results=book_results,
                           form=form,
                           show_recent=show_recent,
                           show_search=show_search,
                           show_results=show_results,
                           points_available=points_available
                           )


@app.route('/my-trades')
@login_required
def my_trades():
    bsdb = get_bsdb()
    user = session['user_num']
    trade_info = bsdb.get_trade_info(user)
    trade_info_dicts = [dict(row) for row in trade_info]

    return render_template('user/my-trades.html',
                           trade_info=trade_info_dicts)


@app.route('/accept-trade/<user_books_id>')
@login_required
def accept_trade(user_books_id):
    print(f"APP: Accept_trade -- Incoming trade acceptance from user {session['user_num']} for book {user_books_id}")
    bsdb = get_bsdb()
    try:
        bsdb.accept_trade(user_books_id)
        print(f"APP: Accept_trade -- Trade successfully accepted.")
        flash("Trade successfully accepted", "success")
    except Exception:
        print(f"APP: Accept_trade -- There was an error in accepting the trade.")
        flash("There was an error in accepting your trade", "warning")
    return redirect(url_for('my_trades'))


@app.route('/reject-trade/<user_books_id>')
@login_required
def reject_trade(user_books_id):
    print(f"APP: Reject_trade -- Incoming trade rejection from user {session['user_num']} for book {user_books_id}")
    bsdb = get_bsdb()
    try:
        bsdb.reject_trade(user_books_id)
        print(
            f"APP: Reject_trade -- Trade successfully rejected.  UserBooks number {user_books_id} is available again.")
        flash("Trade successfully removed", "success")
    except Exception:
        print(f"APP: Reject-trade -- There was an error in rejecting the trade.")
        flash("There was an error in deleting your trade", "warning")
    return redirect(url_for('my_trades'))


@app.route('/login', methods=['GET', 'POST'])
@guest_required
def login():
    form = LoginForm()
    # Checks if input is valid
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        error = None

        db = get_db()
        db.row_factory = sqlite3.Row
        # Username check
        user = db.execute("SELECT * FROM Users WHERE username = ?",
                          (username,)).fetchone()
        if user is None:
            user = db.execute("SELECT * FROM Users WHERE email = ?",
                              (username,)).fetchone()
            if user is None:
                error = "Incorrect username."

        # Password check
        elif user['password'] != password:
            error = "Incorrect password."

        # No errors, login proceeds
        if error is None:
            session.clear()
            session['user_num'] = user['id']
            return redirect(url_for('home'))

        flash(error, 'warning')

    """
    # Simulation of a successful login - sample email and password
    if form.email.data == 'admin@bookswap.com' and form.password.data == 'password':
        flash('You have been logged in!', 'success')
        return redirect(url_for('userHome'))
    else:
        flash('Login Unsuccessful. Please check username and password.', 'danger')
    """
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
                       (form.email.data,)).fetchone() is not None:
            error = 'User {} already exists.  Please try again with a different username, or log in.'.format(
                form.username.data)

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

            print(
                f"Signup: account created for {form.username.data}, with User id {c.lastrowid}")
            flash(f'Account created for {form.email.data}!', 'success')
            session['user_num'] = c.lastrowid

            c.execute("INSERT INTO Wishlists (userId) VALUES (?)", (c.lastrowid,))  # Default wishlist for user
            db.commit()

            return redirect(url_for('account'))
        flash(error, 'warning')
    return render_template('signup.html', form=form)


@app.route('/wishlist')
@login_required
def wishlist():
    bsdb = BookSwapDatabase()
    wishlists = bsdb.get_wishlists_by_userid(session['user_num'])
    wishlist_ids = [row['id'] for row in wishlists]
    book_details = bsdb.get_book_details_for_wishlists(wishlist_ids)

    wishBooks = {}  # maps wishlist IDs to book titles
    for row in book_details:
        if row['wishlistId'] in wishBooks:
            wishBooks[row['wishlistId']].append(row['bookTitle'])
        else:
            wishBooks[row['wishlistId']] = [row['bookTitle']]

    data = {"table_content": wishBooks, "headers": "Wishlists"}
    return render_template('user/wishlist.html', data=data)


@app.route('/add-to-wishlist/<isbn>', methods=['GET'])
@app.route('/add-to-wishlist', methods=['GET'])
@login_required
def add_to_wish(isbn=None):
    db = get_db()
    db.row_factory = sqlite3.Row

    # Queries used for SELECTing and INSERTing
    get_books_isbn_query = 'SELECT * FROM Books WHERE ISBN = ?'
    get_wishlist_books_query = 'SELECT * FROM WishlistsBooks WHERE wishlistId = ? AND bookId = ?'
    insert_wishlist_query = 'INSERT INTO WishlistsBooks (wishlistId, bookId) VALUES (?, ?)'

    # Special path for browse-books route
    if isbn:
        c = db.cursor()
        c.execute(get_books_isbn_query, (isbn,))
        bookId = c.fetchall()[0]['id']

        c.execute(get_wishlist_books_query,
                  (session['user_num'], bookId))

        # if the book was already in the wishlist, don't add it
        if c.fetchall():
            flash("Book already in your wishlist", "warning")
            print(f"APP: AddToWish -- Book {isbn} already in user {session['user_num']}'s wishlist")
        # otherwise, add book to the wishlist
        else:
            c.execute(insert_wishlist_query,
                      (session['user_num'], bookId))
            flash("Book added to your wishlist", "success")
            print(f"APP: AddToWish -- Book {isbn} successfully added to user {session['user_num']}'s wishlist")

        db.commit()
        db.close()
        return redirect('/browse-books')

    data = req.args.get("isbn")
    if data == "":
        return redirect('/wishlist')

    c = db.cursor()
    c.execute(get_books_isbn_query, (data,))
    bookId = c.fetchall()[0]['id']

    c.execute(get_wishlist_books_query,
              (session['user_num'], bookId))

    if not c.fetchall():
        c.execute(insert_wishlist_query,
                  (req.args.get("wishlist"), bookId))
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
    print(wishID, bookID)
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
        print(f"App: Account - request received to change user settings for user {session['user_num']}")
        # Check to make sure form was valid, return form if it was not
        if not account_settings_change_form.validate_on_submit():
            print(f"App: Account -- Settings change form failed validation")
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
            print("App: Account - username is valid")
            try:
                acct.set_account_information(
                    session['user_num'], account_settings_change_form)
                flash("Account information updated.", "success")
                print("App: Account - returning new account info:")
                account_settings = bsdb.get_account_settings(
                    session["user_num"])
                show_account_modal = False
                for key in account_settings.keys():
                    print(f"\t {key}: {account_settings[key]}")
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
        print(f"App.py: Account -- request received to change password for user {session['user_num']}")
        if not password_change_form.validate_on_submit():
            print(f"App: Account -- Password change form failed verification")
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
                flash("Original password was not correct.  Please try again.", "warning")
            else:
                print("App.py: Account -- Original password was entered correctly.")
                try:
                    acct.set_password(session["user_num"],
                                      password_change_form)
                    print("App.py: Account -- New Password set")
                    flash("New Password Sucessfully Set.", "success")
                    show_password_modal = False
                except Exception:
                    print("App.py: Account -- Error setting new password")
                    flash("Error setting new password.  Try again?", "warning")

        except Exception:
            flash("Error determining if the original password is correct.  Try again?", "warning")
            print("App.py: Account -- Error checking original password.")

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
    This method lists a book as available for trade by a user. It involves the following steps:
    - add the book to the backend DB as being available for trade
    - then fetch all books available for trade and redraw the table - so that the new book is now included
    """
    bsdb = get_bsdb()
    if req.get_json().get('request') == 'add':
        # isbn = req.get_json()["isbn"]
        copyquality = req.get_json()["quality"]
        points = req.get_json()["points"]
        book_id = req.get_json()["bookId"]
        user_num = session["user_num"]
        # bsdb.user_add_book_by_isbn(isbn, user_num, copyquality)
        bsdb.user_add_book_by_id(book_id, user_num, copyquality, points)
        rows = bsdb.get_listed_books(user_num)
        copyqualities = bsdb.get_book_qualities()

        # Build the data to be passed to Jinja
        headers = ["Title", "Author", "Quality", "Points", "ISBN"]
        table_content = [[row[header] for header in headers] for row in rows]
        data = {"headers": headers,
                "rows": table_content,
                "caption": "",
                "copyqualities": copyqualities}

        return render_template('user/my-books.html', data=data)


@app.route('/_search-book', methods=['POST'])
@login_required
def search_book():
    """
    This method is POSTed a request with the fields 'isbn', 'author', and 'title', and searches for
    results on the open library API that match these fields. It returns a rendered set of divs to be inserted
    into the html as appropriate.
    """
    bsdb = get_bsdb()
    if req.get_json().get('request') == 'search':
        isbn = req.get_json()["isbn"]
        author = req.get_json()["author"]
        title = req.get_json()["title"]
        # TODO magic number here - number of search results
        search_results = bsdb.search_books_openlibrary(title=title, author=author, isbn=isbn, num_results=5)
        copyqualities = bsdb.get_book_qualities()
        return render_template("snippets/external_search_results.html", search_results=search_results,
                               copyqualities=copyqualities)


@app.route('/removeFromUserLibrary', methods=['GET'])
@login_required
def removeBook():
    db = get_db()
    db.row_factory = sqlite3.Row

    c = db.cursor()

    bookID = req.args.get("bookRem")
    print(bookID)
    c.execute("DELETE FROM UserBooks WHERE id = ?",
              (bookID,))
    db.commit()
    db.close()

    return redirect('/my-books')


@app.route('/my-books')
@login_required
def my_books():
    bsdb = get_bsdb()
    # Get the data of books currently listed
    rows = bsdb.get_listed_books(session['user_num'])
    copyqualities = bsdb.get_book_qualities()

    # Build the data to be passed to Jinja
    headers = ["Title", "Author", "Quality", "Points", "ISBN", "ID"]
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


@app.route('/demo-users')
def demo_users():
    db = get_db()
    # This allows us to access values by column name later on
    db.row_factory = sqlite3.Row
    """
    Step 1: run the SQL query
    Avoid Python's string operations when putting together SQL queries 
    Instead use '?' as a placeholder for each parameter then pass a tuple of parameters as the second argument
    """
    c = db.cursor()
    c.execute("SELECT * FROM Users WHERE city != ?", ("Nashville",))
    """
    Step 2: fetch the results from the SQL query.
    You can treat the cursor as an iterator or call .fetchall() to get a list of all matching rows
    
    Since we set the row factory above, we can access values by index (row[0]) or 
    by column name, case insensitively (row["uSErNAmE"])
    
    Accessing values by column name is useful if we move around columns later on
    """
    rows = c.fetchall()
    table_content = [[row["username"], row["fname"], row["lname"]]
                     for row in rows]
    # Don't forget to close the connection when done with the SQL
    db.close()
    """
    Step 3: pass the data to a jinja template to be rendered
    Here I passed the info as a list of lists,
    and used a loop in the jinja template to create the table
    """
    data = {}
    data["table_content"] = table_content
    data["headers"] = ["Username", "First Name", "Last Name"]
    return render_template("demos/demo-users.html", data=data)


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
