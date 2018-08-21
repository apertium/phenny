"""
test_wikipedia.py - tests for the wikipedia module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import wikipedia
from web import catch_timeout
import wiki


class TestWikipedia(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

        self.term = None
        self.section = None

    def prepare(self):
        if self.section:
            self.text = self.term + '#' + self.section
            url_text = wiki.format_term(self.term) +\
                '#' + wiki.format_section(self.section)
        else:
            self.text = self.term
            url_text = wiki.format_term(self.term)

        self.input.group = lambda x: [None, None, None, self.text, None][x]
        self.url = 'https://en.wikipedia.org/wiki/%s' % url_text

    def check_snippet(self, output):
        self.assertIn(self.url, output)

        for keyword in self.keywords:
            self.assertIn(keyword, output)

    @catch_timeout
    def test_wik(self):
        self.term = "Human back"
        self.prepare()

        wikipedia.wik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        self.keywords = ['human', 'back', 'body', 'buttocks', 'neck']
        self.check_snippet(out)

    @catch_timeout
    def test_wik_fragment(self):
        self.term = "New York City"
        self.section = "Climate"
        self.prepare()

        wikipedia.wik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        self.keywords = ['New York', 'climate', 'humid', 'subtropical']
        self.check_snippet(out)

    @catch_timeout
    def test_wik_invalid(self):
        self.term = "New York City"
        self.section = "Physics"
        self.prepare()

        wikipedia.wik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        message = "No '%s' section found." % self.section
        self.assertEqual(out, '"%s" - %s' % (message, self.url))

    @catch_timeout
    def test_wik_none(self):
        self.term = "Ajgoajh"
        self.prepare()

        wikipedia.wik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        expected = "Can't find anything in Wikipedia for \"%s\"."
        self.assertEqual(out, expected % self.text)
