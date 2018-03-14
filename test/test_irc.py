"""
Tests for phenny's irc.py
"""

import unittest
from mock import call, patch, Mock
import irc


class OriginTest(unittest.TestCase):
    def setUp(self):
        self.bot = Mock()

    def test_server(self):
        source = "foobar.example.com"
        origin = irc.Origin(self.bot, source, [])
        self.assertEqual(origin.host, '')

    def test_privmsg(self):
        source = "Foobar!foo@bar.example.com"
        args = ['PRIVMSG', '#phenny']
        origin = irc.Origin(self.bot, source, args)

        self.assertEqual(origin.nick, 'Foobar')
        self.assertEqual(origin.user, 'foo')
        self.assertEqual(origin.host, 'bar.example.com')
        self.assertEqual(origin.sender, '#phenny')


class BotTest(unittest.TestCase):
    @patch('threading.RLock')
    @patch('asynchat.async_chat')
    def setUp(self, mock_async, mock_thread):
        self.nick = 'foo'
        self.name = 'Phenny'
        self.bot = irc.Bot(self.nick, self.name, '#phenny')

    @patch('irc.Bot.write')
    def test_login(self, mock_write):
        self.bot.verbose = False
        self.bot.handle_connect()

        mock_write.assert_has_calls([
            call(('NICK', self.nick)),
            call(('USER', self.nick, '+iw', '_'), self.name)
            ])

    @patch('irc.Bot.write')
    def test_ping(self, mock_write):
        self.bot.buffer = b"PING"
        self.bot.found_terminator()

        mock_write.assert_called_once_with(('PONG', ''), None)

    @patch('irc.Bot.push')
    def test_msg(self, mock_push):
        self.bot.msg('#phenny', 'hi')

        mock_push.assert_called_once_with(b'PRIVMSG #phenny :hi\r\n')

    @patch('time.sleep') # patch sleep so test runs faster
    @patch('irc.Bot.push')
    def test_msgflood(self, mock_push, mock_sleep):
        self.bot.msg('#phenny', 'flood')
        self.bot.msg('#phenny', 'flood')
        self.bot.msg('#phenny', 'flood')
        self.bot.msg('#phenny', 'flood')
        self.bot.msg('#phenny', 'flood')
        self.bot.msg('#phenny', 'flood')

        mock_push.assert_called_with(b'PRIVMSG #phenny :...\r\n')
        self.assertEqual(mock_sleep.call_count, 5)

    @patch('irc.Bot.msg')
    def test_action(self, mock_msg):
        self.bot.action('foo', 'is')

        mock_msg.assert_called_once_with('foo', '\x01ACTION is\x01')

    @patch('irc.Bot.write')
    def test_notice(self, mock_write):
        notice = "This is a notice!"
        self.bot.proto.notice('jqh', notice)

        mock_write.assert_called_once_with(('NOTICE', 'jqh'), notice)
