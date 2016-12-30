# -*- coding: utf-8 -*-
"""
test_wiktionary.py - tests for the wiktionary module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import re
import unittest
import requests
from mock import MagicMock, Mock
from modules import wiktionary


class TestWiktionary(unittest.TestCase):
    def setUp(self):
        try:
            requests.get('https://en.wiktionary.org').raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            self.skipTest('Wiktionary is down, skipping test.')
        self.phenny = MagicMock()

    def test_wiktionary(self):
        w = wiktionary.wiktionary(self.phenny, 'test')
        self.assertTrue(len(w[1]) > 0)

    def test_wiktionary_none(self):
        w = wiktionary.wiktionary(self.phenny, 'Hell!')
        self.assertEqual(len(w[0]), 0)
        self.assertEqual(len(w[1]), 0)

    def test_w(self):
        input = Mock(group=lambda x: 'test')
        wiktionary.w(self.phenny, input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^test — noun: .*$', out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_w_none(self):
        word = 'boook'
        input = Mock(group=lambda x: word)
        wiktionary.w(self.phenny, input)
        self.phenny.say.assert_called_once_with('Perhaps you meant \'book\'?')
        self.phenny.say.reset_mock()

        word = 'vnuericjnrfu'
        input = Mock(group=lambda x: word)
        wiktionary.w(self.phenny, input)
        self.phenny.say.assert_called_once_with("Couldn't find any definitions for {0}.".format(word))
