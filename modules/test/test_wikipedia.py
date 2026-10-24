"""
test_wikipedia.py - tests for the wikipedia module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from modules.test.command_test import CommandTest
from web import catch_timeout
import wiki


class TestWikipedia(CommandTest, unittest.TestCase):
    modules = ['wikipedia']

    def check_snippet(self, output):
        block = '\n'.join(output)
        self.assertIn(self.url, block)

        for keyword in self.keywords:
            self.assertIn(keyword, block)

    @unittest.skip('Wikipedia formatting has changed; needs new scraper')
    @catch_timeout
    def test_wik(self):
        out = self.run_message('.wik Human Back')

        self.keywords = ['human', 'back', 'body', 'buttocks', 'neck']
        self.check_snippet(out)

    @unittest.skip('Wikipedia formatting has changed; needs new scraper')
    @catch_timeout
    def test_wik_fragment(self):
        out = self.run_message('.wik New York City#Climate')

        self.keywords = ['New York', 'climate', 'humid', 'subtropical']
        self.check_snippet(out)

    @catch_timeout
    def test_wik_invalid(self):
        self.check_response('.wik New York City#Physics',
                            '"No \'Physics\' section found." - https://en.wikipedia.org/wiki/New_York_City#Physics')

    @catch_timeout
    def test_wik_none(self):
        self.check_response('.wik Ajgoajh',
                            "Can't find anything in Wikipedia for \"Ajgoajh\".")
