# BookSwap

**BookSwap** is a web app where users are able to trade copies of used books with each other, accumulating points for sending books and spending them to request books. BookSwap was developed using Python, Flask, Jinja, and SQLite and submitted as part of a large project for the CS 361 course (Software Engineering) at Oregon State University.

**Authors**: 
Ben Wichser, Melissa Lagunas, Ryan McKenzie, Alexa Langen, Nishant Tharani, Phoenix Harris


## User Stories
The following user stories have been implemented as of December 2020: 

- [X] User can sign up. 
- [X] User can login or logout. 
- [X] User can search for a book to list, and list the book for trade.
- [X] User can create a wishlist for their desired books.
- [X] User can search the site's database for any listed books from other users.
- [X] User can request, accept, or decline a trade from other users.
- [X] User can see the selection of currently available books. 
- [X] User can earn points for listing a book. 
- [X] User can use points to trade for a book.

## Installation

Follow these steps to get BookSwap running locally:

1. Clone the repo: `git clone https://github.com/flummoxing/BookSwap`
2. Make sure you are using Python 3 (version 3.8.6 is recommended)
3. Navigate to the folder where you cloned the repo, and install the Python dependencies by running `pip install -r requirements.txt`
4. Run the app: `python app.py` (or `python3 app.py`)
5. Navigate to the provided URL to view the home page (e.g. `http://0.0.0.0:5000/`)
6. **Create the database locally**: before using the app, you must navigate to the `/reset-db` route appended to the homepage. For example, `http://0.0.0.0:5000/reset-db`
7. Go back to the home page and play around! 

## Live demo

As an alternative to installating the latest build, you can use the app [here.](https://bookswap.benwichser.com/)


To simulate a successful login, use the following information.

Username: `admin`

Password: `password`

To interact with multiple users, you can also use the following login info:

Username: `csearl2`

Password: `nAvtnI`






