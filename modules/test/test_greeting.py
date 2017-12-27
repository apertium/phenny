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
        self.input.nick = 'Testsworth'

        self.message = 'Lorem ipsum dolor sit amet'

        self.phenny.config.greetings = {}
        self.phenny.config.greetings[self.input.sender] = self.message

    def test_greeting_binary(self):
        for i in range(256):
            self.phenny.say.reset_mock()
            greeting.greeting(self.phenny, self.input)
            caseless_nick = self.input.nick.casefold()

            if math.log(i + 1, 2) % 1 == 0:
                greetingmessage = self.phenny.config.greetings[self.input.sender]
                greetingmessage = greetingmessage.replace("%name", self.input.nick)
                greetingmessage = greetingmessage.replace("%channel", self.input.sender)

                self.phenny.say.assert_called_once_with(greetingmessage)
            else:
                self.phenny.say.assert_not_called()
