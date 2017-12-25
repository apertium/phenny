"""
Tests for phenny's more.py
"""

import unittest
from mock import MagicMock, patch, call
from modules import more

class TestMore(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.channels = ['#example', '#test']
        self.phenny.messages = {}

        self.input.sender = '#test'
        self.input.nick = 'Testsworth'

        self.messages = [
            'Lorem ipsum dolor sit amet',
            'consetetur sadipscing elitr',
            'sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat',
            'sed diam voluptua',
            'At vero eos et accusam et justo duo dolores et ea rebum',
            'Stet clita kasd gubergren',
        ]

    def create_messages(self, target, num):
        more.add_messages(target, self.phenny, '\n'.join(self.messages[:num+1]), break_up=lambda x, y: x.split('\n'))

    def test_more_self(self):
        self.create_messages(self.input.nick, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, None, None][x]
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_with(self.input.nick + ": " + self.messages[2])

    def test_more_self_one(self):
        self.create_messages(self.input.nick, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, None, '1'][x]
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_with(self.input.nick + ": " + self.messages[2])

    def test_more_self_three(self):
        self.create_messages(self.input.nick, 3)
        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.nick + ": " + message) for message in self.messages[1:4]]
        self.phenny.reply.assert_has_calls(calls)

    def test_more_self_three_two(self):
        self.create_messages(self.input.nick, 5)
        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.nick + ": " + message) for message in self.messages[1:4]]
        calls.append(call("2 messages remaining"))
        self.phenny.reply.assert_has_calls(calls)

    def test_more_admin_self(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, None, None][x]
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_with(self.input.nick + ": " + self.messages[2])

    def test_more_admin_self_one(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, None, '1'][x]
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_with(self.input.nick + ": " + self.messages[2])

    def test_more_admin_self_three(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 3)
        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.nick + ": " + message) for message in self.messages[1:4]]
        self.phenny.reply.assert_has_calls(calls)

    def test_more_admin_self_three_two(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 5)
        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)

        calls = [call(self.input.nick + ": " + message) for message in self.messages[1:4]]
        calls.append(call("2 messages remaining"))
        self.phenny.reply.assert_has_calls(calls)

    def test_more_admin_only(self):
        self.input.admin = True
        self.create_messages(self.input.sender, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, None, None][x]
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_with(self.messages[2])

    def test_more_admin_only_one(self):
        self.input.admin = True
        self.create_messages(self.input.sender, 2)
        more.more(self.phenny, self.input)
        self.input.group = lambda x: [None, None, '1'][x]
        more.more(self.phenny, self.input)
        self.phenny.reply.assert_called_with(self.messages[2])

    def test_more_admin_only_three(self):
        self.input.admin = True
        self.create_messages(self.input.sender, 3)
        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)

        calls = [call(message) for message in self.messages[1:4]]
        self.phenny.reply.assert_has_calls(calls)

    def test_more_admin_only_three_two(self):
        self.input.admin = True
        self.create_messages(self.input.sender, 5)
        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)

        calls = [call(message) for message in self.messages[1:4]]
        calls.append(call("2 messages remaining"))
        self.phenny.reply.assert_has_calls(calls)

    def test_more_admin_both_three(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 3)
        self.create_messages(self.input.sender, 3)
        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)
        more.more(self.phenny, self.input)

        more.more(self.phenny, self.input)
        calls = [call(self.input.nick + ": " + message) for message in self.messages[1:4]]
        self.phenny.reply.assert_has_calls(calls)

        more.more(self.phenny, self.input)
        calls = [call(message) for message in self.messages[1:4]]
        self.phenny.reply.assert_has_calls(calls)

    def test_more_admin_both_three_two(self):
        self.input.admin = True
        self.create_messages(self.input.nick, 5)
        self.create_messages(self.input.sender, 5)

        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)
        calls = [call(self.input.nick + ": " + message) for message in self.messages[1:4]]
        calls.append(call("2 messages remaining"))
        self.phenny.reply.assert_has_calls(calls)

        self.input.group = lambda x: [None, None, '2'][x]
        more.more(self.phenny, self.input)

        self.input.group = lambda x: [None, None, '3'][x]
        more.more(self.phenny, self.input)
        calls = [call(message) for message in self.messages[1:4]]
        calls.append(call("2 messages remaining"))
        self.phenny.reply.assert_has_calls(calls)
