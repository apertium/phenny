"""
test_slogan.py - tests for the slogan module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import slogan
from web import catch_timeout


class TestSlogan(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    @catch_timeout
    def test_sloganize(self):
        out = slogan.sloganize('slogan')
        if out == '\x15\x03\x01':
            self.skipTest('Server SSL error')
        self.assertRegex(out, ".*slogan.*")

    @catch_timeout
    def test_slogan(self):
        self.input.group.return_value = 'slogan'
        slogan.slogan(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        if out == '\x15\x03\x01':
            self.skipTest('Server SSL error')
        self.assertRegex(out, ".*slogan.*")

    @catch_timeout
    def test_slogan_none(self):
        self.input.group.return_value = None
        slogan.slogan(self.phenny, self.input)
        self.phenny.say.assert_called_once_with(
            "You need to specify a word; try .slogan Granola")
