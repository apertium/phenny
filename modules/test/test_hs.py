"""
test_hs.py - tests for the hokie stalker module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import hs
from web import catch_timeout


class TestHs(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    @catch_timeout
    def test_search(self):
        data = hs.search('john')
        self.assertTrue(len(data) >= 1)
        self.assertIn('uid', data[0])
        self.assertIn('cn', data[0])

    @catch_timeout
    def test_single(self):
        self.input.group.return_value = 'marchany'
        hs.hs(self.phenny, self.input)
        pattern = re.compile(
            '^.* - http://search\.vt\.edu/search/person\.html\?person=\d+$',
            flags=re.UNICODE)
        out = self.phenny.reply.call_args[0][0]
        self.assertRegex(out, pattern)

    @catch_timeout
    def test_multi(self):
        self.input.group.return_value = 'john'
        hs.hs(self.phenny, self.input)
        pattern = re.compile(
            '^Multiple results found; try http://search\.vt\.edu/search/people\.html\?q=.*$',
            flags=re.UNICODE)
        out = self.phenny.reply.call_args[0][0]
        self.assertRegex(out, pattern)

    @catch_timeout
    def test_2char(self):
        self.input.group.return_value = 'hs'
        hs.hs(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.phenny.reply.assert_called_once_with("No results found")

    @catch_timeout
    def test_none(self):
        self.input.group.return_value = 'THIS_IS_NOT_A_REAL_SEARCH_QUERY'
        hs.hs(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.phenny.reply.assert_called_once_with("No results found")
