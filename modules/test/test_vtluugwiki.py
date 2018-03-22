"""
test_vtluugwiki.py - tests for the VTLUUG wiki module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import vtluugwiki
from web import catch_timeout
import wiki


class TestVtluugwiki(unittest.TestCase):

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

        self.input.group = lambda x: [None, self.text][x]
        self.url = 'https://vtluug.org/wiki/%s' % url_text

    def check_snippet(self, output):
        self.assertIn(self.url, output)

        for keyword in self.keywords:
            self.assertIn(keyword, output)

    @catch_timeout
    def test_vtluug(self):
        self.term = "VT-Wireless"
        self.prepare()

        vtluugwiki.vtluug(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        self.keywords = ['campus', 'wireless', 'networks']
        self.check_snippet(out)

    @catch_timeout
    def test_vtluug_fragment(self):
        self.term = "EAP-TLS"
        self.section = "netctl"
        self.prepare()

        vtluugwiki.vtluug(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        self.keywords = ['Arch', 'Linux', 'netctl']
        self.check_snippet(out)

    @catch_timeout
    def test_vtluug_invalid(self):
        self.term = "EAP-TLS"
        self.section = "netcfg"
        self.prepare()

        vtluugwiki.vtluug(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        message = "No '%s' section found." % self.section
        expected = '"%s" - https://vtluug.org/wiki/%s'
        self.assertEqual(out, expected % (message, self.text))

    @catch_timeout
    def test_vtluug_none(self):
        self.term = "Ajgoajh"
        self.prepare()

        vtluugwiki.vtluug(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]

        expected = "Can't find anything in the VTLUUG Wiki for \"%s\"."
        self.assertEqual(out, expected % self.text)
