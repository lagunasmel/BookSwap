from flask import Flask, render_template, url_for
from db_connector import get_db#, close_connection
import sqlite3
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
# Secret Key for Flask Forms security
app.config['SECRET_KEY'] = '31c46d586e5489fa9fbc65c9d8fd21ed'

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    form = RegistrationForm()
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    return render_template('signup.html', form=form)


@app.route('/wishlist')
def wishlist():
    db = get_db()
    db.row_factory = sqlite3.Row

    # Select user based on username, using generic for now
    c = db.cursor()
    c.execute("SELECT id FROM Users WHERE username = ?", ("afoan2", ))

    # Fetch the user's id 
    userID = c.fetchall()[0]["id"]


    # Using the user's id, select their wishlists
    c.execute("SELECT * FROM Wishlists WHERE userId = ?", (userID, ))
    wishlists = [ row["id"] for row in c.fetchall() ]

    # Build IN query string
    values = ""
    for wish in wishlists:
        values += str(wish) + ", "

    values = values[:-2]

    # Select book names per wishlist
    c.execute("SELECT wishlistId, Books.title FROM WishlistsBooks w INNER JOIN Books ON w.bookId = Books.id WHERE wishlistId IN (?)", (values, ))

    # Map wishlists to books for user
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
    return render_template('wishlist.html', data=data)


@app.route('/account')
def account():
    return render_template('account.html')


@app.route('/demo-users')
def demo_users():
    db = get_db()
    db.row_factory = sqlite3.Row  # This allows us to access values by column name later on
    """
    Step 1: run the SQL query
    Avoid Python's string operations when putting together SQL queries 
    Instead use '?' as a placeholder for each parameter then pass a tuple of parameters as the second argument
    """
    c = db.cursor()
    c.execute("SELECT * FROM Users WHERE city != ?", ("Nashville", ))
    """
    Step 2: fetch the results from the SQL query.
    You can treat the cursor as an iterator or call .fetchall() to get a list of all matching rows
    
    Since we set the row factory above, we can access values by index (row[0]) or 
    by column name, case insensitively (row["uSErNAmE"])
    
    Accessing values by column name is useful if we move around columns later on
    """
    rows = c.fetchall()
    table_content = [[row["username"], row["fname"], row["lname"]] for row in rows]
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
    return render_template("demo-users.html", data=data)








@app.route('/reset-db')
def reset_db():
    """
    A "secret" route for resetting database specs and content.
    """
    with app.app_context():
        db = get_db()
        with app.open_resource('DatabaseSpecs/database-definition-queries.sql',
                mode = 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    return "Database reset :)"

if __name__ == '__main__':
    """
    `host` keyword arg added by Ben to make it work on his server.  It seems to 
    work the same on his local machine.  Maybe others can test too?
    """
    app.run(host='0.0.0.0', debug=True)

