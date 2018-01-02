"""
test_imdb.py - tests for the imdb module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules.imdb import imdb_search, imdb, API_KEY
from tools import is_up


class TestImdb(unittest.TestCase):
    def setUp(self):
        if not is_up('http://www.omdbapi.com'):
            self.skipTest('OMDb server is down, skipping test.')

        if API_KEY is None:
            self.skipTest('No API key provided for OMDbAPI, skipping test.')

        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_imdb_search(self):
        data = imdb_search('Hackers')
        self.assertIn('Plot', data)
        self.assertIn('Title', data)
        self.assertIn('Year', data)
        self.assertIn('imdbID', data)

    def test_imdb(self):
        self.input.group.return_value = 'Antitrust'
        imdb(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        pattern = re.compile(
            r'^.* \(.*\): .* http://imdb.com/title/[a-z\d]+$',
            flags=re.UNICODE)
        self.assertRegex(out, pattern)

    def test_imdb_none(self):
        self.input.group.return_value = None
        imdb(self.phenny, self.input)
        self.phenny.say.assert_called_once_with(".imdb what?")
