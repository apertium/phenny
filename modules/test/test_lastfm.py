"""
test_lastfm.py - tests for the lastfm module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules.lastfm import now_playing
from tools import is_up


class TestLastfm(unittest.TestCase):
    user1 = 'test'
    user2 = 'telnoratti'

    def setUp(self):
        if not is_up('https://ws.audioscrobbler.com'):
            self.skipTest('LastFM server is down, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_now_playing(self):
        self.input.group.return_value = self.user1
        now_playing(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^{0} listened to ".+" by .+ on .+ .*$'.format(self.user1),
                     out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_now_playing_sender(self):
        self.input.group.return_value = ''
        self.input.nick = self.user1
        now_playing(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^{0} listened to ".+" by .+ on .+ .*$'.format(self.user1),
                     out, flags=re.UNICODE)
        self.assertTrue(m)
