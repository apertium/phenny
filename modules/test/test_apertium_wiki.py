import unittest
from mock import MagicMock
from modules import apertium_wiki
from web import catch_timeout, get
from datetime import date, timedelta
import wiki
import re


class TestApertiumWiki(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.channels = ["#apertium"]
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
    def test_logs_today(self):
        self.input.group = lambda x: [None, 'today'][x]
        apertium_wiki.logs(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        string_check = "Log at " in out
        if string_check:
            url = out[7:]
            out_check = str(date.today()) in out
        self.assertTrue(string_check and out_check)


    @catch_timeout
    def test_logs_yesterday(self):
        self.input.group = lambda x: [None, 'yesterday'][x]
        apertium_wiki.logs(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        string_check = "Log at " in out

        if string_check:
            url = out[7:]
            out_check = str(date.today() - timedelta(1)) in out
        self.assertTrue(string_check and out_check)

    @catch_timeout
    def test_logs_last_week(self):
        self.input.group = lambda x: [None, 'last monday'][x]
        apertium_wiki.logs(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        string_check = "Log at " in out

        if string_check:
            url = out[7:]
            last_mon = str(date.today()-timedelta(7-date.today().weekday()))
            out_check = last_mon in out
            self.assertTrue(string_check and out_check)

    @catch_timeout
    def test_logs_good_date(self):
        self.input.group = lambda x: [None, '10/23/2018'][x]
        apertium_wiki.logs(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        string_check = "Log at " in out
        if string_check:
            url = out[7:]
            day_query = str(date(2018, 10, 23))
            out_check = day_query in out
        self.assertTrue(string_check and out_check)

    @catch_timeout
    def test_logs_bad_date(self):
        self.input.group = lambda x: [None, '99/99/9999'][x]
        apertium_wiki.logs(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        string_check = "Log at " in out

        if string_check:
            url = out[7:]
            day_query = str(date(9999, 99, 99))
            out_check = day_query in out
        self.assertFalse(string_check and out_check)
