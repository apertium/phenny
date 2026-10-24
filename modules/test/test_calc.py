# coding=utf-8
"""
test_calc.py - tests for the calc module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from modules.test.command_test import CommandTest

class TestCalc(CommandTest, unittest.TestCase):
    modules = ['calc']

    def test_c(self):
        self.check_response('.c 5*5', '25')

    def test_c_sqrt(self):
        self.check_response('.c 4^(1/2)', '2')

    def test_c_none(self):
        self.check_response('.c aif', 'Sorry, no result.')

    def test_c_equation(self):
        self.check_response('.c 4*x+4=x*5', '4')

    def test_c_sin(self):
        self.check_response('.c log(90)', '4.499809670330265')
