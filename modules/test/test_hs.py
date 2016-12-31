"""
test_hs.py - tests for the hokie stalker module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules.hs import search, hs
from tools import is_up


# these tests are probably skipped because the app domain used in hs.py seem to
# be currently non-functional
class TestHs(unittest.TestCase):
    def setUp(self):
        for url in ['https://webapps.middleware.vt.edu', 'http://search.vt.edu']:
            if not is_up(url):
                self.skipTest('One or more hokie domains are down, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_search(self):
        data = search('john')
        self.assertTrue(len(data) >= 1)
        self.assertIn('uid', data[0])
        self.assertIn('cn', data[0])

    def test_single(self):
        self.input.group.return_value = 'marchany'
        hs(self.phenny, self.input)
        pattern = re.compile(
            '^.* - http://search\.vt\.edu/search/person\.html\?person=\d+$',
            flags=re.UNICODE)
        out = self.phenny.reply.call_args[0][0]
        self.assertRegex(out, pattern)

    def test_multi(self):
        self.input.group.return_value = 'john'
        hs(self.phenny, self.input)
        pattern = re.compile(
            '^Multiple results found; try http://search\.vt\.edu/search/people\.html\?q=.*$',
            flags=re.UNICODE)
        out = self.phenny.reply.call_args[0][0]
        self.assertRegex(out, pattern)

    def test_2char(self):
        self.input.group.return_value = 'hs'
        hs(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.phenny.reply.assert_called_once_with("No results found")

    def test_none(self):
        self.input.group.return_value = 'THIS_IS_NOT_A_REAL_SEARCH_QUERY'
        hs(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.phenny.reply.assert_called_once_with("No results found")
