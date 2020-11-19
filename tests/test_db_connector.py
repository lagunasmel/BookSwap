import pytest
import db_connector as dbc
from flask import Flask, render_template, url_for, flash, redirect, session, g


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    yield app


def test_search_books_openlibrary_1(app):
    with app.app_context():
        bsdb = dbc.BookSwapDatabase()
        out = bsdb.search_books_openlibrary(title="lord", author="tolkien")
        print([o['id'] for o in out])


def test_search_books_openlibrary_5(app):
    with app.app_context():
        bsdb = dbc.BookSwapDatabase()
        out = bsdb.search_books_openlibrary(title="harry potter", author="rowling", num_results=5)
        print([o['id'] for o in out])
