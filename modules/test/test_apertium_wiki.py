import unittest
from mock import MagicMock
from modules import apertium_wiki
from web import catch_timeout
from datetime import date, timedelta
from random import randint
import wiki
import requests


class TestApertiumWiki(unittest.TestCase):

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

        self.input.group = lambda x: [None, None, self.text, None][x]
        self.url = 'http://wiki.apertium.org/wiki/%s' % url_text

    def check_snippet(self, output):
        self.assertIn(self.url, output)

        for keyword in self.keywords:
            self.assertIn(keyword, output)

    @catch_timeout
    def test_awik(self):
        self.term = "Apertium Turkic"
        self.prepare()

        apertium_wiki.awik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        self.keywords = ['Apertium', 'Turkic', 'working', 'group']
        self.check_snippet(out)

    @catch_timeout
    def test_awik_fragment(self):
        self.term = "Apertium Turkic"
        self.section = "Translation pairs"
        self.prepare()

        apertium_wiki.awik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        self.keywords = ['work', 'systems', 'Turkic', 'languages']
        self.check_snippet(out)

    @catch_timeout
    def test_awik_invalid(self):
        self.term = "Apertium Turkic"
        self.section = "Doner"
        self.prepare()

        apertium_wiki.awik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        message = "No '%s' section found." % self.section
        self.assertEqual(out, '"%s" - %s' % (message, self.url))

    @catch_timeout
    def test_awik_none(self):
        self.term = "Ajgoajh"
        self.prepare()

        apertium_wiki.awik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        expected = "Can't find anything in the Apertium Wiki for \"%s\"."
        self.assertEqual(out, expected % self.text)

    @catch_timeout
    def test_logs(self):
        day = str(date.today() - timedelta(randint(1, 1000)))
        status_code = requests.get(apertium_wiki.endpoints['log']+day+".log").status_code

        self.assertEqual(status_code, 200)
