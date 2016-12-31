"""
test_wikipedia.py - tests for the wikipedia module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import wikipedia
from tools import is_up


class TestWikipedia(unittest.TestCase):
    def makegroup(*args):
        args2 = [] + list(args)
        def group(x):
            if x > 0 and x <= len(args2):
                return args2[x - 1]
            else:
                return None
        return group

    def setUp(self):
        if not is_up('https://en.wikipedia.org'):
            self.skipTest('Wikipedia is down, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_wik(self):
        self.input.group = lambda x: ['', 'wik', '', 'Human back'][x]
        wikipedia.wik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - https:\/\/en\.wikipedia\.org\/wiki\/Human_back$',
                out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_wik_fragment(self):
        term = "New York City#Climate"
        self.input.group = lambda x: ['', 'wik', '', term][x]
        wikipedia.wik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - https:\/\/en\.wikipedia\.org\/wiki\/New_York_City#Climate$',
                out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_wik_none(self):
        term = "Ajgoajh"
        self.input.group = lambda x: ['', 'wik', '', term][x]
        wikipedia.wik(self.phenny, self.input)
        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "Wikipedia for \"{0}\".".format(term))
