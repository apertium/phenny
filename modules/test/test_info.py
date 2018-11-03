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

    def test_help_invalid(self):
        self.input.group = lambda x: [None, 'notacommand'][x]
        self.input.sender = "user"
        info.help(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("Sorry, I don't know that command." in out)

    def test_help_channel(self):
        self.input.group = lambda x: [None, ''][x]
        self.input.sender = "#channel"
        info.help(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        help_string = "Hey there, I'm a friendly bot for #apertium. Say \".help\" to me in private for a list of my commands or check out my help page at"
        self.assertTrue(help_string in out)

    def test_help_pm(self):
        self.input.sender = "username"
        self.input.channels = []
        self.input.group = lambda x: [None, False][x]
        info.help(self.phenny, self.input)
        out = self.phenny.say.call_count
        self.assertTrue(out == 3)  # calls for 'hey there..', 'for help with...', 'talk to my owner

    def test_stats(self):
        info.stats(self.phenny, self.input)
        out = self.phenny.say.call_count
        self.assertTrue(out == 3)  # calls for most-used, power-users, power-chans
