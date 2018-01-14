"""
test_lastfm.py - tests for the lastfm module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import lastfm
from web import catch_timeouts


@catch_timeouts
class TestLastfm(unittest.TestCase):
    user1 = 'test'
    user2 = 'telnoratti'

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_now_playing(self):
        self.input.group.return_value = self.user1
        lastfm.now_playing(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^{0} listened to ".+" by .+ on .+ .*$'.format(self.user1),
                     out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_now_playing_sender(self):
        self.input.group.return_value = ''
        self.input.nick = self.user1
        lastfm.now_playing(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^{0} listened to ".+" by .+ on .+ .*$'.format(self.user1),
                     out, flags=re.UNICODE)
        self.assertTrue(m)
