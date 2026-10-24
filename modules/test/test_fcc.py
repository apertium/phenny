"""
test_fcc.py - tests for the fcc module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from modules.test.command_test import CommandTest

class TestFCC(CommandTest, unittest.TestCase):
    modules = ['fcc']

    def test_fcc_help(self):
        self.check_response('.fcc',
                            '.fcc <callsign> - Look up a callsign issued by the FCC.')

    def test_fcc(self):
        out = self.message_response('.fcc W3AJ')
        self.assertIn('SWARTHMORE', out)

    def test_fcc_none(self):
        out = self.message_response('.fcc NOTACODE')
        self.assertIn('No results found', out)
