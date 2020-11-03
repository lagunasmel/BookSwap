from flask import Flask, render_template, url_for
from db_connector import get_db#, close_connection

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')


@app.route('/account')
def account():
    return render_template('account.html')


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

