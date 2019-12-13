"""
Tests for phenny's greeting.py
"""

import unittest
import math
from mock import MagicMock
from modules import greeting, logger

class TestGreeting(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.host = 'irc.freenode.net'

        logger.setup(self.phenny)
        greeting.setup(self.phenny)

        self.input.sender = '#test'

        self.phenny.config.greetings = {}
        self.phenny.config.greet_delay = 0

    def test_greeting_binary(self):
        self.input.nick = 'Testsworth'

        message = 'Lorem ipsum dolor sit amet'
        self.phenny.config.greetings[self.input.sender] = message

        for i in range(256):
            self.phenny.msg.reset_mock()
            greeting.greeting(self.phenny, self.input)
            caseless_nick = self.input.nick.casefold()

            if math.log2(i + 1) % 1 == 0:
                greetingmessage = message
                greetingmessage = greetingmessage.replace("%name", self.input.nick)
                greetingmessage = greetingmessage.replace("%channel", self.input.sender)

                if i == 0:
                    self.phenny.msg.assert_called_with(self.input.nick, greetingmessage)
                else:
                    self.phenny.msg.assert_called_once_with(self.input.nick, greetingmessage)
            else:
                self.phenny.msg.assert_not_called()

    def test_greeting_remove_m_hint(self):
        self.input.nick = 'Test[m]worth'

        greeting.greeting(self.phenny, self.input)

        hint = "Please consider removing [m] from your IRC nick. See http://wiki.apertium.org/wiki/IRC/Matrix#Remove_.5Bm.5D_from_your_IRC_nick for details. Reply .dismiss to prevent this message from appearing again."
        self.phenny.msg.assert_called_once_with(self.input.nick, self.input.nick + ": " + hint)
