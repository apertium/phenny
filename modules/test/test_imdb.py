"""
test_imdb.py - tests for the imdb module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import imdb
from web import catch_timeout


class TestImdb(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    @catch_timeout
    def test_imdb_search(self):
        data = imdb.imdb_search('Hackers')
        self.assertIn('Plot', data)
        self.assertIn('Title', data)
        self.assertIn('Year', data)
        self.assertIn('imdbID', data)

    @catch_timeout
    def test_imdb(self):
        self.input.group.return_value = 'Antitrust'
        imdb.imdb(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        pattern = re.compile(
            r'^.* \(.*\): .* http://imdb.com/title/[a-z\d]+$',
            flags=re.UNICODE)
        self.assertRegex(out, pattern)

    @catch_timeout
    def test_imdb_none(self):
        self.input.group.return_value = None
        imdb.imdb(self.phenny, self.input)
        self.phenny.say.assert_called_once_with(".imdb what?")
