"""
test_eleda.py - tests for the eleda module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from mock import MagicMock
from modules import eleda


class TestEleda(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_follow(self):
        self.input.group = lambda x: [None, 'firespeaker eng-spa'][x]
        eleda.follow(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        eleda.follows = []
        self.assertTrue("now following" in out)

    def test_unfollow_invalid(self):
        self.user = MagicMock()
        self.user.nick = "firespeaker"
        eleda.follows = [self.user]
        self.input.group = lambda x: [None, 'not_firespeaker'][x]
        eleda.unfollow(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Sorry, you aren't following that user" in out)

    def test_following(self):
        self.user = MagicMock()
        self.user.nick = "firespeaker"
        self.user2 = MagicMock()
        self.user2.nick = "begiak"
        eleda.follows = [self.user, self.user2]
        eleda.following(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("firespeaker" in out and "begiak" in out)

    def test_no_one_following(self):
        eleda.follows = []
        eleda.following(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("No one is being followed at the moment." in out)
