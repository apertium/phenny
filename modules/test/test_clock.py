"""
test_clock.py - tests for the clock module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import re
import datetime
import unittest
from mock import MagicMock, Mock, patch
from modules.clock import f_time, beats, yi, tock, npl
from nose.tools import nottest


class TestClock(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    @patch('time.time')
    @nottest
    def test_time(self, mock_time):
        mock_time.return_value = 1338674651
        input = Mock(group=lambda x: 'EDT')
        f_time(self.phenny, input)

        self.phenny.msg.called_once_with('#phenny',
                "Sat, 02 Jun 2012 18:04:11 EDT")

    @patch('time.time')
    def test_beats_zero(self, mock_time):
        mock_time.return_value = 0
        beats(self.phenny, None)

        self.phenny.say.assert_called_with('@041')

    @patch('time.time')
    def test_beats_normal(self, mock_time):
        mock_time.return_value = 369182
        beats(self.phenny, None)

        self.phenny.say.assert_called_with('@314')

    @patch('time.time')
    def test_yi_normal(self, mock_time):
        mock_time.return_value = 369182
        yi(self.phenny, None)

        self.phenny.say.assert_called_with('Not yet...')

    @patch('time.time')
    def test_yi_soon(self, mock_time):
        mock_time.return_value = 1339419000
        yi(self.phenny, None)

        self.phenny.say.assert_called_with('Soon...')

    @patch('time.time')
    def test_yi_now(self, mock_time):
        mock_time.return_value = 1339419650
        yi(self.phenny, None)

        self.phenny.say.assert_called_with('Yes! PARTAI!')

    def test_tock(self):
        tock(self.phenny, None)

        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - tycho.usno.navy.mil$',
                out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_npl(self):
        npl(self.phenny, None)

        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - ntp1.npl.co.uk$',
                out, flags=re.UNICODE)
        self.assertTrue(m)
