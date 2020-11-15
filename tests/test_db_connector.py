import pytest
import db_connector as dbc
from flask import Flask, render_template, url_for, flash, redirect, session, g


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    yield app


def test_db(app):
    with app.app_context():
        bsdb = dbc.BookSwapDatabase()
        