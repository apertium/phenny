import unittest
from modules.test.command_test import CommandTest
from mock import MagicMock
from modules import apertium_wiki
from web import catch_timeout, get
from datetime import date, timedelta
import wiki


class TestApertiumWiki(CommandTest, unittest.TestCase):
    modules = ['apertium_wiki']

    def add_config(self):
        self.config.channels = ['#apertium']

    def prepare(self, section, term):
        if section:
            self.text = term + '#' + section
            url_text = wiki.format_term(term) +\
                '#' + wiki.format_section(section)
        else:
            self.text = term
            url_text = wiki.format_term(term)

        self.url = 'https://wiki.apertium.org/wiki/%s' % url_text
        return self.message_response('.awik '+self.text)

    def check_snippet(self, output):
        self.assertIn(self.url, output)

        for keyword in self.keywords:
            self.assertIn(keyword, output)

    @catch_timeout
    def test_awik(self):
        out = self.prepare(None, 'Apertium Turkic')
        self.keywords = ['Apertium', 'Turkic', 'working', 'group']
        self.check_snippet(out)

    @catch_timeout
    def test_awik_fragment(self):
        out = self.prepare('Translation pairs', 'Apertium Turkic')
        self.keywords = ['work', 'systems', 'Turkic', 'languages']
        self.check_snippet(out)

    @catch_timeout
    def test_awik_invalid(self):
        out = self.prepare('Doner', 'Apertium Turkic')
        message = 'No \'Doner\' section found.'
        self.assertEqual(out, '"%s" - %s' % (message, self.url))

    @catch_timeout
    def test_awik_none(self):
        out = self.prepare(None, 'Ajgoajh')
        expected = 'Can\'t find anything in the Apertium Wiki for "%s".'
        self.assertEqual(out, expected % self.text)

    def test_logs_today(self):
        out = self.message_response('.logs today', nick='bob')
        self.assertIn('Log at ', out)
        self.assertIn(str(date.today()), out)

    def test_logs_yesterday(self):
        out = self.message_response('.logs yesterday', nick='bob')
        self.assertIn('Log at ', out)
        self.assertIn(str(date.today() - timedelta(1)), out)

    def test_logs_last_week(self):
        out = self.message_response('.logs last monday', nick='bob')
        self.assertIn('Log at ', out)
        last_mon = str(date.today() + timedelta(-7 - date.today().weekday()))
        self.assertIn(last_mon, out)

    def test_logs_good_date(self):
        out = self.message_response('.logs 10/23/2025')
        self.assertIn('Log at ', out)
        self.assertIn('2025-10-23', out)

    def test_logs_bad_date(self):
        out = self.message_response('.logs 99/99/9999')
        self.assertNotIn('Log at ', out)
        self.assertNotIn('9999', out)

    def test_logs_no_date(self):
        out = self.message_response('.logs')
        self.assertIn('Log at ', out)
        self.assertNotRegex(out, r'\.log$')
