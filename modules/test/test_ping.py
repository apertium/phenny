"""
test_ping.py - tests for the ping module
author: nu11us <work.willeggleston@gmail.com>
"""
import unittest
from modules.test.command_test import CommandTest

class TestPing(CommandTest, unittest.TestCase):
    modules = ['ping']

    def test_get_guests_user(self):
        out = self.message_response('.getguests', nick='admin')
        self.assertEqual(out, "{''}")

    def test_interjection(self):
        self.phenny.nick = 'begiak'
        self.check_response('begiak!', nick='user', expected='user!')
