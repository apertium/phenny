"""
test_info.py - tests for the info module
author: nu11us <work.willeggleston@gmail.com>
"""
import re
import unittest
from mock import MagicMock
from modules import info
from web import catch_timeout


class TestInfo(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def resetPhenny(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_help_invalid(self):
        self.resetPhenny()
        self.input.group = lambda x: [None, 'notacommand'][x]
        self.input.sender = "user"
        info.help(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("Sorry, I don't know that command." in out)

    def test_help_channel(self):
        self.resetPhenny()
        self.input.group = lambda x: [None, ''][x]
        self.input.sender = "#channel"
        info.help(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("to me in private" in out)

    def test_help_pm(self):
        self.resetPhenny()
        self.input.sender = "username"
        self.input.channels = []
        self.input.group = lambda x: [None, False][x]
        info.help(self.phenny, self.input)
        out = self.phenny.say.call_count
        self.assertTrue(out == 3)
