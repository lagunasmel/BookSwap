import sqlite3
from book_search import BookSearch
from account import AccountSettings
from flask import Flask, render_template, url_for, flash, redirect, session, g
from flask import request as req
from db_connector import get_db, BookSwapDatabase, get_bsdb
from forms import (RegistrationForm, LoginForm, BookSearchForm,
                   AccountSettingsChangeForm, PasswordChangeForm)
from auth import login_required, guest_required

app = Flask(__name__)
# Secret Key for Flask Forms security
app.config['SECRET_KEY'] = '31c46d586e5489fa9fbc65c9d8fd21ed'


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
def learnHow():
    return render_template('learn-how.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/request-book', methods=['GET'])
def requestBook():
    db = get_db()
    db.row_factory = sqlite3.Row

    c = db.cursor()

    userBooksId = req.args.get('userBooksId')
    lister = req.args.get('listing_user')
    isbn = req.args.get('requested_book')
    requester = session['user_num']

    c.execute("INSERT INTO Trades (userRequestedId, userBookId, statusId) VALUES (?, ?, ?)",
              (requester, userBooksId, 2))

    db.commit()

    return redirect('/browse-books')


@app.route('/browse-books', methods=['GET', 'POST'])
def browse_books():
    form = BookSearchForm()
    bsdb = get_bsdb()
    recent_books = bsdb.get_recent_additions(5)
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

    print("App.py: BrowseBooks:")
    print(f"\t recent_books: {recent_books}")
    print(f"\t book_results: {book_results}")
    print(f"\t form: {form}")
    return render_template('browse-books.html',
                           recent_books=recent_books,
                           book_results=book_results,
                           form=form,
                           show_recent=show_recent,
                           show_search=show_search,
                           show_results=show_results
                           )


@app.route('/my-trades')
def my_trades():
    db = get_db()
    c = db.cursor()

    user = session["user_num"]
    c.execute("SELECT * FROM Trades WHERE userRequestedId = ?", (user,))

    trades = c.fetchall()

    c.execute(
        "SELECT * FROM Trades INNER JOIN UserBooks ON Trades.userBookId = UserBooks.id WHERE UserBooks.userId = ?",
        (user,))

    pending = c.fetchall()

    return render_template('user/my-trades.html',
                           trades=trades,
                           pending=pending)


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
    db = get_db()
    db.row_factory = sqlite3.Row

    # Select user based on username, using generic for now
    c = db.cursor()
    # c.execute("SELECT id FROM Users WHERE username = ?", (session["user_num"],))

    # Fetch the user's id
    # userID = c.fetchall()[0]["id"]

    # Using the user's id, select their wishlists
    c.execute("SELECT * FROM Wishlists WHERE userId = ?",
              (session["user_num"],))

    wishlists = [row["id"] for row in c.fetchall()]

    # Build IN query string
    values = ""
    for wish in wishlists:
        values += str(wish) + ", "

    values = values[:-2]

    # Select book names per wishlist
    c.execute(
        "SELECT wishlistId, Books.title FROM WishlistsBooks w INNER JOIN Books ON w.bookId = Books.id WHERE wishlistId IN (?)",
        (values,))
    for row in c.fetchall():
        print([i for i in row])
    # Map wishlists to books for user
    c.execute(
        "SELECT wishlistId, Books.title FROM WishlistsBooks w INNER JOIN Books ON w.bookId = Books.id WHERE wishlistId IN (?)",
        (values,))
    wishBooks = {}
    for row in c.fetchall():
        if row[0] in wishBooks:
            wishBooks[row[0]].append(row[1])
        else:
            wishBooks[row[0]] = [row[1]]

    db.close()

    data = {}
    data["table_content"] = wishBooks
    data["headers"] = "Wishlists"
    return render_template('user/wishlist.html', data=data)


@app.route('/addToWishlist/<isbn>', methods=['GET'])
@app.route('/addToWishlist', methods=['GET'])
@login_required
def addToWish(isbn=None):
    db = get_db()
    db.row_factory = sqlite3.Row

    # Special path for browse-books route
    if isbn:
        c = db.cursor()
        c.execute("SELECT * FROM Books WHERE ISBN = ?", (isbn,))
        bookId = c.fetchall()[0]['id']

        c.execute("SELECT * FROM WishlistsBooks WHERE wishlistId = ? AND bookId = ?",
                  (session['user_num'], bookId))

        if not c.fetchall():
            c.execute("INSERT INTO WishlistsBooks (wishlistId, bookId) VALUES (?, ?)",
                      (session['user_num'], bookId))

        db.commit()
        db.close()
        return redirect('/browse-books')

    data = req.args.get("isbn")
    if data == "":
        return redirect('/wishlist')

    c = db.cursor()
    c.execute("SELECT * FROM Books WHERE ISBN = ?", (data,))
    bookId = c.fetchall()[0]['id']

    c.execute("SELECT * FROM WishlistsBooks WHERE wishlistId = ? AND bookId = ?",
              (session['user_num'], bookId))

    if not c.fetchall():
        c.execute("INSERT INTO WishlistsBooks (wishlistId, bookId) VALUES (?, ?)",
                  (req.args.get("wishlist"), bookId))
    db.commit()
    db.close()

    return redirect('/wishlist')


@app.route('/removeFromWishlist', methods=['GET'])
@login_required
def removeWish():
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
    elif (req.method == 'POST' and password_change_form.submit.data):
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
    bsdb = get_bsdb()
    if req.get_json().get('request') == 'add':
        isbn = req.get_json()["isbn"]
        copyquality = req.get_json()["quality"]
        user_num = session["user_num"]
        bsdb.user_add_book_by_isbn(isbn, user_num, copyquality)
        rows = bsdb.get_listed_books(user_num)
        copyqualities = bsdb.get_book_qualities()

        # Build the data to be passed to Jinja
        headers = ["Title", "Author", "Quality", "ISBN"]
        table_content = [[row[header] for header in headers] for row in rows]
        data = {"headers": headers,
                "rows": table_content,
                "caption": "",
                "copyqualities": copyqualities}

        return render_template('user/my-books.html', data=data)


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
    headers = ["Title", "Author", "Quality", "ISBN", "ID"]
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
