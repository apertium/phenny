"""
test_info.py - tests for the info module
author: nu11us <work.willeggleston@gmail.com>
"""
import unittest
from modules.test.command_test import CommandTest

class TestInfo(CommandTest, unittest.TestCase):
    modules = ['info']

    def test_help_invalid(self):
        self.check_response('.help notacommand', channel='user',
                            expected="Sorry, I don't know that command.")

    def test_help_channel(self):
        self.phenny.config.helpurl = 'potato'
        self.check_response('.help whatever', channel='#stuff',
                            expected="Hey there, I'm a friendly bot for #apertium. Say \".help\" to me in private for a list of my commands or check out my help page at potato.")

    def test_help_pm(self):
        out = self.run_message('.help', channel='user')
        self.assertEqual(len(out), 3) # lines for 'hey there..', 'for help with...', 'talk to my owner

    def test_stats(self):
        out = self.run_message('.stats')
        self.assertEqual(len(out), 3) # calls for most-used, power-users, power-chans
