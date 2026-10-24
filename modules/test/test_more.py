"""
Tests for phenny's more.py
"""

import unittest
from modules.test.command_test import CommandTest

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

class TestMore(CommandTest, unittest.TestCase):
    modules = ['more']

    def add_config(self):
        self.config.channels = ['#example', '#test']

    def setUp(self):
        super().setUp()
        self.get_module().delete_all(self.phenny, target='Testsworth')
        self.get_module().delete_all(self.phenny, target='#test')

        self.messages = [
            'Lorem ipsum dolor sit amet',
            'consetetur sadipscing elitr',
            'sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat',
            'sed diam voluptua',
            'At vero eos et accusam et justo duo dolores et ea rebum',
            'Stet clita kasd gubergren',
        ]

    def create_messages(self, target, num, tag='test'):
        self.get_module().add_messages(self.phenny, target, self.messages[:num], tag=tag)
        self.phenny.write_queue = []
        self.target = target

    def fetch(self, admin, owner, count, tag, index, remaining):
        nick = 'user'
        if owner:
            nick = 'owner'
        elif admin:
            nick = 'admin'
        out = self.run_message(f'.more {count or 1} {tag or ""}', nick=nick,
                               channel=self.target)
        prefix = f'PRIVMSG {self.target} :'
        if self.target == '#test' and nick == 'user':
            self.assertEqual(out, [prefix+nick+': Only admins can use .more on channels.'])
        elif index == 0 and remaining == 0:
            self.assertEqual(out, [prefix+nick+': No more queued messages'])
        elif not count or count == 1:
            if self.target == 'user':
                prefix += self.target + ': '
            message = prefix+self.messages[index]
            if remaining:
                message += " (%s remaining)" % remaining
            self.assertEqual(out, [message])
        else:
            messages = [prefix+m for m in self.messages[index:index+(count or 1)]]
            if remaining:
                messages.append(prefix+f'{remaining} message(s) remaining')

    def test_more_user_user(self):
        self.create_messages('user', 3)

        self.fetch(False, False, None, None, 1, 1)

        self.fetch(False, False, None, None, 2, 0)

    def test_more_user_user_one(self):
        self.create_messages('user', 3)

        self.fetch(False, False, None, None, 1, 1)

        self.fetch(False, False, 1, None, 2, 0)

    def test_more_user_user_three(self):
        self.create_messages('user', 4)

        self.fetch(False, False, 3, None, 1, 0)

    def test_more_user_user_three_two(self):
        self.create_messages('user', 6)

        self.fetch(False, False, 3, None, 1, 0)

    def test_more_user_user_none(self):
        self.target = 'user'
        self.fetch(False, False, None, None, 0, 0)

    def test_more_user_channel(self):
        self.create_messages('#test', 3)

        self.fetch(False, False, None, None, 0, 0)

    def test_more_admin_user(self):
        self.create_messages('user', 3)

        self.fetch(True, False, None, None, 1, 1)

        self.fetch(True, False, None, None, 2, 0)

    def test_more_admin_user_one(self):
        self.create_messages('user', 3)

        self.fetch(True, False, None, None, 1, 1)

        self.fetch(True, False, 1, None, 2, 0)

    def test_more_admin_user_three(self):
        self.create_messages('user', 4)

        self.fetch(True, False, 3, None, 1, 0)

    def test_more_admin_user_three_two(self):
        self.create_messages('user', 6)

        self.fetch(True, False, 3, None, 1, 2)

    def test_more_admin_channel(self):
        self.create_messages('#test', 3)

        self.fetch(True, False, None, None, 1, 1)

        self.fetch(True, False, None, None, 2, 0)

    def test_more_admin_channel_one(self):
        self.create_messages('#test', 3)

        self.fetch(True, False, None, None, 1, 1)

        self.fetch(True, False, 1, None, 2, 0)

    def test_more_admin_channel_three(self):
        self.create_messages('#test', 4)

        self.fetch(True, False, 3, None, 1, 0)

    def test_more_admin_channel_three_two(self):
        self.create_messages('#test', 6)

        self.fetch(True, False, 3, None, 1, 2)

    def test_more_admin_both_three(self):
        self.create_messages('user', 4)
        self.create_messages('#test', 4)

        self.fetch(True, False, 3, None, 1, 0)

        self.fetch(True, False, 3, None, 1, 0)

    def test_more_admin_both_three_two(self):
        self.create_messages('user', 6)
        self.create_messages('#test', 6)

        self.fetch(True, False, 3, None, 1, 2)

        self.fetch(True, False, 2, None, 4, 0)

        self.fetch(True, False, 3, None, 1, 2)

    def test_more_admin_both_none(self):
        self.target = 'user'
        self.fetch(False, False, None, None, 0, 0)
