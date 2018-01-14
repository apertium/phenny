# -*- coding: utf-8 -*-
"""
test_wiktionary.py - tests for the wiktionary module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import wiktionary
from web import catch_timeouts


@catch_timeouts
class TestWiktionary(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_wiktionary(self):
        w = wiktionary.wiktionary(self.phenny, 'test')
        self.assertTrue(len(w[1]) > 0)

    def test_wiktionary_none(self):
        w = wiktionary.wiktionary(self.phenny, 'Hell!')
        self.assertEqual(len(w[0]), 0)
        self.assertEqual(len(w[1]), 0)

    def test_w(self):
        self.input.group.return_value = 'test'
        wiktionary.w(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^test — noun: .*$', out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_w_none(self):
        word = 'boook'
        self.input.group.return_value = word
        wiktionary.w(self.phenny, self.input)
        out = self.phenny.say.call_args_list
        self.assertEqual('Perhaps you meant \'book\'?', out[0][0][0])
        self.assertTrue(re.match(r'^book — noun:', out[1][0][0], flags=re.UNICODE))
        self.phenny.say.reset_mock()

        word = 'vnuericjnrfu'
        self.input.group.return_value = word
        wiktionary.w(self.phenny, self.input)
        self.phenny.say.assert_called_once_with("Couldn't find any definitions for {0}.".format(word))
