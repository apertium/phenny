"""
Tests for phenny's greeting.py
"""

import unittest
from modules.test.command_test import CommandTest
import math

class TestGreeting(CommandTest, unittest.TestCase):
    modules = ['greeting', 'logger']

    def add_config(self):
        self.config.greetings = {}
        self.config.greet_delay = 0

    def test_greeting_binary(self):
        message = 'Lorem ipsum dolor sit amet'
        self.phenny.config.greetings['#apertium'] = message

        nick = 'Testworth'
        caseless_nick = 'testworth'
        for i in range(256):
            out = self.run_event(':Testworth!blah@blah JOIN #apertium')

            if math.log2(i + 1) % 1 == 0:
                greetingmessage = message
                greetingmessage = greetingmessage.replace("%name", nick)
                greetingmessage = greetingmessage.replace("%channel", '#apertium')

                self.assertIn('PRIVMSG Testworth :'+greetingmessage, out)
            else:
                self.assertEqual(out, [])

    def test_greeting_remove_m_hint(self):
        out = self.run_event(':Test[m]worth!blah@blah JOIN #apertium')
        hint = "Please consider removing [m] from your IRC nick. See https://wiki.apertium.org/wiki/IRC/Matrix#Remove_.5Bm.5D_from_your_IRC_nick for details. Reply .dismiss to prevent this message from appearing again."
        self.assertEqual(out, ['PRIVMSG Test[m]worth :Test[m]worth: '+hint])
