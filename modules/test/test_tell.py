"""
Tests for phenny's tell.py
"""

import unittest
import datetime
from mock import MagicMock
from modules import tell

class TestTell(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.host = 'irc.freenode.net'

        self.input = MagicMock()
        tell.setup(self.phenny)

    def create_reminder(self, teller):
        timenow = datetime.datetime.utcnow().strftime('%d %b %Y %H:%MZ')
        self.phenny.reminders[teller] = [(teller, 'do', timenow, 'something')]

    def test_messageAlert(self):
        self.input.sender = '#testsworth'
        self.input.nick = 'Testsworth'

        self.create_reminder(self.input.nick)
        tell.messageAlert(self.phenny, self.input)

        text = ': You have messages. Say something, and I\'ll read them out.'
        self.phenny.say.assert_called_once_with(self.input.nick + text)

    def test_fremind_valid(self):
        self.input.nick = 'Testsworth'
        self.input.groups = lambda: ['tests', 'eat a cake']

        tell.f_remind(self.phenny, self.input, 'ask')
        responses = {'I\'ll pass that on when tests is around.', 'yeah, yeah', 'yeah, sure, whatever'}
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out in responses)

    def test_fremind_edgecase(self):
        self.input.nick = 'Testsworth'
        self.input.groups = lambda: ['me', 'eat a cake']

        tell.f_remind(self.phenny, self.input, 'ask')
        self.phenny.say.assert_called_once_with('Hey, I\'m not as stupid as Monty you know!')

    def test_ftell(self):
        self.input.nick = 'Testsworth'
        self.input.groups = lambda: ['tests', 'eat a cake']

        tell.f_tell(self.phenny, self.input)
        responses = {'I\'ll pass that on when tests is around.', 'yeah, yeah', 'yeah, sure, whatever'}
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out in responses)

    def test_formatreminder(self):
        dt = datetime.datetime.utcnow().strftime('%d %b %Y %H:%MZ')
        ret = tell.formatReminder(['tests', 'ask', dt, 'to eat cake'], 'Testsworth', None)

        dt = dt[len(datetime.datetime.utcnow().strftime('%d %b')) + 1:]
        dt = dt.replace(datetime.datetime.utcnow().strftime('%Y '), '')
        self.assertTrue(ret == 'Testsworth: %s <tests> ask Testsworth to eat cake' % dt)
