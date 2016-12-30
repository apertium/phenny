"""
test_wikipedia.py - tests for the wikipedia module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import re
import unittest
import requests
from mock import MagicMock, Mock
from modules import wikipedia


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
        try:
            requests.get('https://en.wikipedia.org').raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            self.skipTest('Wikipedia is down, skipping test.'.format(name))
        self.phenny = MagicMock()

    def test_wik(self):
        input = Mock(group=self.makegroup('', 'Human back'))
        wikipedia.wik(self.phenny, input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - https:\/\/en\.wikipedia\.org\/wiki\/Human_back$',
                out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_wik_fragment(self):
        term = "New York City#Climate"
        input = Mock(group=self.makegroup('', term))
        wikipedia.wik(self.phenny, input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - https:\/\/en\.wikipedia\.org\/wiki\/New_York_City#Climate$',
                out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_wik_none(self):
        term = "Ajgoajh"
        input = Mock(group=self.makegroup('', term))
        wikipedia.wik(self.phenny, input)
        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "Wikipedia for \"{0}\".".format(term))
