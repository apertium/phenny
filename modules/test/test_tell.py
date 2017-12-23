"""
Tests for phenny's tell.py
"""

import unittest
import datetime
import os
from mock import MagicMock, patch
from modules import tell

class TestTell(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.nick = 'phenny'

        alias_file = os.path.expanduser('~/.phenny/aliases.db')
        os.makedirs(os.path.dirname(alias_file), exist_ok=True)

        self.phenny.alias_filename = alias_file

    def create_alias(self, alias):
        self.input.group = lambda x: ['', 'add', alias][x]
        tell.alias(self.phenny, self.input)
        tell.aliasPairMerge(self.phenny, self.input.nick, alias)

    def create_reminder(self, teller):
        timenow = datetime.datetime.utcnow().strftime('%d %b %Y %H:%MZ')
        self.phenny.reminders[teller] = [(teller, 'do', timenow, 'something')]

    def test_messageAlert(self):
        self.input.sender = '#testsworth'
        self.input.nick = 'Testsworth'

        aliases = ['tester', 'testing', 'testmaster']
        self.phenny.reminders = {}

        for alias in aliases:
            self.create_alias(alias)
            self.create_reminder(alias)

        tell.messageAlert(self.phenny, self.input)

        text = ': You have messages. Say something, and I\'ll read them out.'
        self.phenny.say.assert_called_once_with(self.input.nick + text)
