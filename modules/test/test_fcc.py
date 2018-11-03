"""
test_fcc.py - tests for the fcc module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from mock import MagicMock
from modules import fcc as fcc_module
from threading import Thread


class TestFCC(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_fcc_help(self):
        self.input.group = lambda x: [None, None, None][x]
        fcc_module.fcc(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("Look up a callsign issued by the FCC" in out) 

    def test_fcc(self):
        self.input.group = lambda x: [None, None, "W3AJ"][x]
        fcc_module.fcc(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("SWARTHMORE" in out)

    def test_fcc_none(self):
        self.input.group = lambda x: [None, None, "NOTACODE"][x]
        fcc_module.fcc(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("No results found" in out)

