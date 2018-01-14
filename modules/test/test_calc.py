# coding=utf-8
"""
test_calc.py - tests for the calc module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import calc


class TestCalc(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_c(self):
        self.input.group.return_value = '5*5'
        calc.c(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('25')

    def test_c_sqrt(self):
        self.input.group.return_value = '4^(1/2)'
        calc.c(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('2')

    def test_c_none(self):
        self.input.group.return_value = 'aif'
        calc.c(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('Sorry, no result.')

    def test_c_equation(self):
        self.input.group.return_value = '4*x+4=x*5'
        calc.c(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('4')

    def test_c_sin(self):
        self.input.group.return_value = 'log(90)'
        calc.c(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('4.499809670330265')
