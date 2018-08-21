"""
Tests for phenny's bot.py
"""

import unittest
from mock import call, patch, Mock
import bot


class BotTest(unittest.TestCase):
    @patch('bot.Phenny.setup')
    def setUp(self, mock_setup):
        class MockConfig(object):
            nick = 'phenny'
            password = 'nickserv_pass'
            name = 'Phenny'
            host = 'irc.example.com'
            port = 6667
            ssl = False
            ipv6 = True
            channels = ['#phenny']
            owner = 'phenny_owner'
            admins = [owner, 'phenny_admin']
            prefix = '.'

        self.bot = bot.Phenny(MockConfig)

    def test_input(self):
        class MockOrigin(object):
            nick = 'sock_puppet'
            sender = '#phenny'

        origin = MockOrigin()
        text = "Are you ready for phenny?"
        match = Mock()
        args = ('#phenny', )
        cmdinput = self.bot.input(origin, text, match, args)

        self.assertEqual(cmdinput.sender, origin.sender)
        self.assertEqual(cmdinput.nick, origin.nick)
        self.assertEqual(cmdinput.bytes, text)
        self.assertEqual(cmdinput.group, match.group)
        self.assertEqual(cmdinput.groups, match.groups)
        self.assertEqual(cmdinput.args, args)
        self.assertEqual(cmdinput.admin, False)
        self.assertEqual(cmdinput.owner, False)

    def test_owner(self):
        class MockOrigin(object):
            nick = 'phenny_owner'
            sender = '#phenny'

        origin = MockOrigin()
        text = "Are you ready for phenny?"
        match = Mock()
        event = "PRIVMSG"
        args = ('#phenny', )
        cmdinput = self.bot.input(origin, text, match, args)

        self.assertEqual(cmdinput.owner, True)

    def test_admin(self):
        class MockOrigin(object):
            nick = 'phenny_admin'
            sender = '#phenny'

        origin = MockOrigin()
        text = "Are you ready for phenny?"
        match = Mock()
        event = "PRIVMSG"
        args = ('#phenny', )
        cmdinput = self.bot.input(origin, text, match, args)

        self.assertEqual(cmdinput.admin, True)
