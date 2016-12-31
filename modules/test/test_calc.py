# coding=utf-8
"""
test_calc.py - tests for the calc module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules.calc import c
from tools import is_up


class TestCalc(unittest.TestCase):
    def setUp(self):
        if not is_up('https://duckduckgo.com'):
            self.skipTest('DuckDuckGo is down, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_c(self):
        self.input.group.return_value = '5*5'
        c(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('25')

    def test_c_sqrt(self):
        self.input.group.return_value = '4^(1/2)'
        c(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('2')

    def test_c_scientific(self):
        self.input.group.return_value = '2^64'
        c(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('1.84467440737096 * 10^19')

    def test_c_none(self):
        self.input.group.return_value = 'aif'
        c(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Sorry, no result.')
