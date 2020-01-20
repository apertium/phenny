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

    def test_fremind_toolong(self):
        self.input.nick = 'Testsworth'
        self.input.groups = lambda: ['testerrrrrrrrrrrrrrrrr', 'eat a cake']

        tell.f_remind(self.phenny, self.input, 'ask')
        self.phenny.reply.assert_called_once_with('That nickname is too long.')

    def test_fremind_edgecase(self):
        self.input.nick = 'Testsworth'
        self.input.groups = lambda: ['me', 'eat a cake']

        tell.f_remind(self.phenny, self.input, 'ask')
        self.phenny.say.assert_called_once_with('Hey, I\'m not as stupid as Monty you know!')

    def test_formatreminder(self):
        dt = datetime.datetime.utcnow().strftime('%d %b %Y %H:%MZ')
        ret = tell.formatReminder(['tests', 'ask', dt, 'to eat cake'], 'Testsworth', None)

        dt = dt[len(datetime.datetime.utcnow().strftime('%d %b')) + 1:]
        dt = dt.replace(datetime.datetime.utcnow().strftime('%Y '), '')
        self.assertTrue(ret == 'Testsworth: %s <tests> ask Testsworth to eat cake' % dt)