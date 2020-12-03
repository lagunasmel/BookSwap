# ReadMe - BookSwap

**BookSwap** is an upcoming web app where users will be able to trade copies of used books with each other, accumulating points for sending books and spending them to request books. BookSwap is a work in progress, and is currently being developed using Python, Flask, Jinja, and SQLite.

## Installation

Follow these steps to get BookSwap running locally:

1. Clone the repo: `git clone https://github.com/flummoxing/BookSwap`
2. Make sure you are using Python 3 (version 3.8.6 is recommended)
3. Navigate to the folder where you cloned the repo, and install the Python dependencies by running `pip install -r requirements.txt`
4. Run the app: `python app.py` (or `python3 app.py`)
5. Navigate to the provided URL to view the home page (e.g. `http://0.0.0.0:5000/`)
6. **Create the database locally**: before using the app, you must navigate to the `/reset-db` route appended to the homepage. For example, `http://0.0.0.0:5000/reset-db`
7. Go back to the home page and play around! 

To simulate a successful login, use the following information.

Username: `admin@bookswap.com`

Password: `password`



## Live demo

As an alternative to installating the latest build, you can use the app at [bookswap.benwichser.com].


[bookswap.benwichser.com]: https://bookswap.benwichser.com









