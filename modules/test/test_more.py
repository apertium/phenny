"""
Tests for phenny's more.py
"""

import unittest
from mock import MagicMock, call
from modules import more

def assert_call(mock, *args):
    mock.assert_called_once_with(*args)
    mock.reset_mock()

def assert_calls(mock, *args):
    mock.assert_has_calls(*args)
    mock.reset_mock()

def formatting(message, target):
    if not target.startswith('#'):
        message = target + ": " + message
    return message

class TestMore(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.channels = ['#example', '#test']
        self.phenny.config.host = 'irc.oftc.net'

        self.input = MagicMock()
        self.input.sender = '#test'
        self.input.nick = 'Testsworth'

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

    def create_messages(self, target, num, tag='test'):
        more.add_messages(self.phenny, target, self.messages[:num], tag=tag)

    def fetch(self, admin, owner, count, tag):
        self.input.admin = admin
        self.input.owner = owner
        self.input.group = lambda x: [None, count, tag][x]
        more.more(self.phenny, self.input)

    def assert_msg(self, target, index, remaining):
        message = formatting(self.messages[index], target)
        if remaining:
            message += " (%s remaining)" % remaining
        assert_call(self.phenny.say, message)

    def assert_msgs(self, target, start, end, remaining):
        calls = [call(formatting(message, target)) for message in self.messages[start:end]]
        if remaining:
            calls.append(call(str(remaining) + " message(s) remaining"))
        assert_calls(self.phenny.say, calls)

    def test_more_user_user(self):
        self.create_messages(self.input.nick, 3)

        self.fetch(False, False, None, None)
        self.assert_msg(self.input.nick, 1, 1)

        self.fetch(False, False, None, None)
        self.assert_msg(self.input.nick, 2, 0)

    def test_more_user_user_one(self):
        self.create_messages(self.input.nick, 3)

        self.fetch(False, False, None, None)
        self.assert_msg(self.input.nick, 1, 1)

        self.fetch(False, False, 1, None)
        self.assert_msg(self.input.nick, 2, 0)

    def test_more_user_user_three(self):
        self.create_messages(self.input.nick, 4)

        self.fetch(False, False, 3, None)
        self.assert_msgs(self.input.nick, 1, 4, 0)

    def test_more_user_user_three_two(self):
        self.create_messages(self.input.nick, 6)

        self.fetch(False, False, 3, None)
        self.assert_msgs(self.input.nick, 1, 4, 0)

    def test_more_user_user_none(self):
        self.fetch(False, False, None, None)
        assert_call(self.phenny.reply, "No more queued messages")

    def test_more_user_channel(self):
        self.create_messages(self.input.sender, 3)

        self.fetch(False, False, None, None)
        assert_call(self.phenny.reply, "Only admins can use .more on channels.")

    def test_more_admin_user(self):
        self.create_messages(self.input.nick, 3)

        self.fetch(True, False, None, None)
        self.assert_msg(self.input.nick, 1, 1)

        self.fetch(True, False, None, None)
        self.assert_msg(self.input.nick, 2, 0)

    def test_more_admin_user_one(self):
        self.create_messages(self.input.nick, 3)

        self.fetch(True, False, None, None)
        self.assert_msg(self.input.nick, 1, 1)

        self.fetch(True, False, 1, None)
        self.assert_msg(self.input.nick, 2, 0)

    def test_more_admin_user_three(self):
        self.create_messages(self.input.nick, 4)

        self.fetch(True, False, 3, None)
        self.assert_msgs(self.input.nick, 1, 4, 0)

    def test_more_admin_user_three_two(self):
        self.create_messages(self.input.nick, 6)

        self.fetch(True, False, 3, None)
        self.assert_msgs(self.input.nick, 1, 4, 2)

    def test_more_admin_channel(self):
        self.create_messages(self.input.sender, 3)

        self.fetch(True, False, None, None)
        self.assert_msg(self.input.sender, 1, 1)

        self.fetch(True, False, None, None)
        self.assert_msg(self.input.sender, 2, 0)

    def test_more_admin_channel_one(self):
        self.create_messages(self.input.sender, 3)

        self.fetch(True, False, None, None)
        self.assert_msg(self.input.sender, 1, 1)

        self.fetch(True, False, 1, None)
        self.assert_msg(self.input.sender, 2, 0)

    def test_more_admin_channel_three(self):
        self.create_messages(self.input.sender, 4)

        self.fetch(True, False, 3, None)
        self.assert_msgs(self.input.sender, 1, 4, 0)

    def test_more_admin_channel_three_two(self):
        self.create_messages(self.input.sender, 6)

        self.fetch(True, False, 3, None)
        self.assert_msgs(self.input.sender, 1, 4, 2)

    def test_more_admin_both_three(self):
        self.create_messages(self.input.nick, 4)
        self.create_messages(self.input.sender, 4)

        self.fetch(True, False, 3, None)
        self.assert_msgs(self.input.nick, 1, 4, 0)

        self.fetch(True, False, 3, None)
        self.assert_msgs(self.input.sender, 1, 4, 0)

    def test_more_admin_both_three_two(self):
        self.create_messages(self.input.nick, 6)
        self.create_messages(self.input.sender, 6)

        self.fetch(True, False, 3, None)
        self.assert_msgs(self.input.nick, 1, 4, 2)

        self.fetch(True, False, 2, None)
        self.assert_msgs(self.input.nick, 4, 6, 0)

        self.fetch(True, False, 3, None)
        self.assert_msgs(self.input.sender, 1, 4, 2)

    def test_more_admin_both_none(self):
        self.fetch(False, False, None, None)
        assert_call(self.phenny.reply, "No more queued messages")
