"""
Tests for phenny's greeting.py
"""

import unittest
import math
import os
from mock import MagicMock, patch, call
from modules import greeting, posted, logger

class TestGreeting(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.host = 'irc.freenode.net'

        os.makedirs(os.path.expanduser('~/.phenny'), exist_ok=True)

        logger.setup(self.phenny)
        greeting.setup(self.phenny)

        self.input.sender = '#test'

        self.phenny.config.greetings = {}

    def test_greeting_binary(self):
        self.input.nick = 'Testsworth'

        message = 'Lorem ipsum dolor sit amet'
        self.phenny.config.greetings[self.input.sender] = message

        for i in range(256):
            self.phenny.say.reset_mock()
            greeting.greeting(self.phenny, self.input)
            caseless_nick = self.input.nick.casefold()

            if math.log2(i + 1) % 1 == 0:
                greetingmessage = message
                greetingmessage = greetingmessage.replace("%name", self.input.nick)
                greetingmessage = greetingmessage.replace("%channel", self.input.sender)

                self.phenny.say.assert_called_once_with(greetingmessage)
            else:
                self.phenny.say.assert_not_called()

    def test_greeting_remove_m_hint(self):
        self.input.nick = 'Test[m]worth'

        greeting.greeting(self.phenny, self.input)

        hint = "Consider removing [m] from your IRC nick! See http://wiki.apertium.org/wiki/IRC/Matrix#Remove_.5Bm.5D_from_your_IRC_nick for details."
        self.phenny.msg.assert_called_once_with(self.input.nick, self.input.nick + ": " + hint)
