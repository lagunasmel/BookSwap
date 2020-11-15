from unittest import TestCase
import unittest
from db_connector import search_books_openlibrary


class TestSearch(TestCase):
    def test_lotr(self):
        results = search_books_openlibrary(title="Lord", author="Tolkien")
        self.assertGreaterEqual(len(results), 1)
