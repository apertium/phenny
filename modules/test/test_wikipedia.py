"""
test_wikipedia.py - tests for the wikipedia module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import wikipedia, posted
from web import catch_timeouts


@catch_timeouts
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
        self.phenny = MagicMock(variables=['posted'], nick='phenny')
        self.phenny.config.host = 'irc.freenode.net'
        posted.DB_DIR = '.'
        posted.setup(self.phenny)
        self.input = MagicMock(sender='#phenny', nick='tester')

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
