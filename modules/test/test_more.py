"""
Tests for phenny's more.py
"""

import unittest
from mock import MagicMock, call
from modules import more

class TestMore(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.channels = ['#example', '#test']
        self.phenny.config.host = 'irc.freenode.net'

        self.input = MagicMock()
        self.input.sender = '#test'
        self.input.nick = 'Testsworth'
        self.input.group = lambda x: [None, None, None][x]
        self.input.admin = False
        self.input.owner = False

        more.setup(self.phenny)
        more.delete_all(self.phenny, target=self.input.nick)
        more.delete_all(self.phenny, target=self.input.sender)

        self.messages = [
            'Lorem ipsum dolor sit amet',
            'consetetur sadipscing elitr',
            'sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat',
            'sed diam voluptua',
            'At vero eos et accusam et justo duo dolores et ea rebum',
            'Stet clita kasd gubergren',
        ]

    def create_messages(self, target, num):
        # TODO: test tagging system
        more.add_messages(self.phenny, target, self.messages[:num+1], tag='test')

    def test_more_user_user(self):
        self.create_messages(self.input.nick, 2)
        more.more(self.phenny, self.input)
        more.more(self.phenny, self.input)
        self.phenny.msg.assert_called_with(self.input.sender, self.input.nick + ": " + self.messages[2])

    def test_more_user_user_one(self):
        self.create_messages(self.input.nick, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, '1', None][x]
        more.more(self.phenny, self.input)
        self.phenny.msg.assert_called_with(self.input.sender, self.input.nick + ": " + self.messages[2])

    def test_more_user_user_three(self):
        self.create_messages(self.input.nick, 3)
        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.sender, self.input.nick + ": " + message) for message in self.messages[1:4]]
        self.phenny.msg.assert_has_calls(calls)

    def test_more_user_user_three_two(self):
        self.create_messages(self.input.nick, 5)
        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.sender, self.input.nick + ": " + message) for message in self.messages[1:4]]
        calls.append(call(self.input.sender, "2 message(s) remaining"))
        self.phenny.msg.assert_has_calls(calls)

    def test_more_user_user_none(self):
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("No more queued messages")

    def test_more_user_channel(self):
        self.create_messages(self.input.sender, 2)
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("No more queued messages")

    def test_more_admin_user(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 2)
        more.more(self.phenny, self.input)
        more.more(self.phenny, self.input)
        self.phenny.msg.assert_called_with(self.input.sender, self.input.nick + ": " + self.messages[2])

    def test_more_admin_user_one(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, '1', None][x]
        more.more(self.phenny, self.input)
        self.phenny.msg.assert_called_with(self.input.sender, self.input.nick + ": " + self.messages[2])

    def test_more_admin_user_three(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 3)
        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.sender, self.input.nick + ": " + message) for message in self.messages[1:4]]
        self.phenny.msg.assert_has_calls(calls)

    def test_more_admin_user_three_two(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 5)
        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.sender, self.input.nick + ": " + message) for message in self.messages[1:4]]
        calls.append(call(self.input.sender, "2 message(s) remaining"))
        self.phenny.msg.assert_has_calls(calls)

    def test_more_admin_channel(self):
        self.input.admin = True
        self.create_messages(self.input.sender, 2)
        more.more(self.phenny, self.input)
        more.more(self.phenny, self.input)
        self.phenny.msg.assert_called_with(self.input.sender, self.messages[2])

    def test_more_admin_channel_one(self):
        self.input.admin = True
        self.create_messages(self.input.sender, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, '1', None][x]
        more.more(self.phenny, self.input)
        self.phenny.msg.assert_called_with(self.input.sender, self.messages[2])

    def test_more_admin_channel_three(self):
        self.input.admin = True
        self.create_messages(self.input.sender, 3)
        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.sender, message) for message in self.messages[1:4]]
        self.phenny.msg.assert_has_calls(calls)

    def test_more_admin_channel_three_two(self):
        self.input.admin = True
        self.create_messages(self.input.sender, 5)
        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.sender, message) for message in self.messages[1:4]]
        calls.append(call(self.input.sender, "2 message(s) remaining"))
        self.phenny.msg.assert_has_calls(calls)

    def test_more_admin_both_three(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 3)
        self.create_messages(self.input.sender, 3)
        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)
        more.more(self.phenny, self.input)

        more.more(self.phenny, self.input)
        calls = [call(self.input.sender, self.input.nick + ": " + message) for message in self.messages[1:4]]
        self.phenny.msg.assert_has_calls(calls)

        more.more(self.phenny, self.input)
        calls = [call(self.input.sender, message) for message in self.messages[1:4]]
        self.phenny.msg.assert_has_calls(calls)

    def test_more_admin_both_three_two(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 5)
        self.create_messages(self.input.sender, 5)

        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)
        calls = [call(self.input.sender, self.input.nick + ": " + message) for message in self.messages[1:4]]
        calls.append(call(self.input.sender, "2 message(s) remaining"))
        self.phenny.msg.assert_has_calls(calls)

        self.input.group = lambda x: [None, '2', None][x]
        more.more(self.phenny, self.input)

        self.input.group = lambda x: [None, '3', None][x]
        more.more(self.phenny, self.input)
        calls = [call(self.input.sender, message) for message in self.messages[1:4]]
        calls.append(call(self.input.sender, "2 message(s) remaining"))
        self.phenny.msg.assert_has_calls(calls)

    def test_more_admin_both_none(self):
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("No more queued messages")
