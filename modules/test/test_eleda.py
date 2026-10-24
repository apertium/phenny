"""
test_eleda.py - tests for the eleda module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from modules.test.command_test import CommandTest

class TestEleda(CommandTest, unittest.TestCase):
    modules = ['eleda']

    def test_follow(self):
        out = self.message_response('.follow firespeaker eng-spa')
        self.assertIn('now following', out)
        self.get_module().follows = []

    def test_unfollow_invalid(self):
        self.check_response('.unfollow not_firespeaker',
                            nick='test',
                            expected="test: Sorry, you aren't following that user!")

    def test_following(self):
        obj = self.get_module().Eleda
        self.get_module().follows = [obj('bob', 'firespeaker', 'a-b'),
                                     obj('bob', 'begiak', 'c-b')]
        out = self.message_response('.following')
        self.assertIn('firespeaker', out)
        self.assertIn('begiak', out)
        self.get_module().follows = []

    def test_no_one_following(self):
        self.check_response('.following', nick='bob',
                            expected='bob: No one is being followed at the moment.')
