"""
test_urbandict.py - tests for the urban dictionary module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from modules.test.command_test import CommandTest
from web import catch_timeout

class TestUrbandict(CommandTest, unittest.TestCase):
    modules = ['urbandict']

    @catch_timeout
    def test_result(self):
        out = self.message_response('.urb slemp')
        self.assertRegex(out, r'^.* - http://www\.urbandictionary\.com/define\.php\?term=.*$')

    @catch_timeout
    def test_none(self):
        self.check_response(
            '.urb __no_word_here__',
            'No results found for __no_word_here__')
