"""
test_clock.py - tests for the clock module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock, patch
from modules import clock
from web import catch_timeout


@patch('time.time')
class TestClock(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    @unittest.skip('Test requires timezone and city databases, which are currently tricky to '
                   'properly configure on Travis CI.')
    def test_time(self, mock_time):
        mock_time.return_value = 1338674651
        self.input.group.return_value = 'EDT'
        clock.f_time(self.phenny, self.input)
        self.phenny.msg.assert_called_once_with('#phenny',
                "Sat, 02 Jun 2012 18:04:11 EDT")

    def test_beats_zero(self, mock_time):
        mock_time.return_value = 0
        clock.beats(self.phenny, None)
        self.phenny.say.assert_called_with('@041')

    def test_beats_normal(self, mock_time):
        mock_time.return_value = 369182
        clock.beats(self.phenny, None)
        self.phenny.say.assert_called_with('@314')

    def test_yi_normal(self, mock_time):
        mock_time.return_value = 369182
        clock.yi(self.phenny, None)
        self.phenny.say.assert_called_with('Not yet...')

    def test_yi_soon(self, mock_time):
        mock_time.return_value = 1339419000
        clock.yi(self.phenny, None)
        self.phenny.say.assert_called_with('Soon...')

    def test_yi_now(self, mock_time):
        mock_time.return_value = 1339419650
        clock.yi(self.phenny, None)
        self.phenny.say.assert_called_with('Yes! PARTAI!')

    @catch_timeout
    def test_tock(self, mock_time):
        clock.tock(self.phenny, None)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - tycho.usno.navy.mil$',
                out, flags=re.UNICODE)
        self.assertTrue(m)

    @catch_timeout
    def test_npl(self, mock_time):
        clock.npl(self.phenny, None)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - ntp1.npl.co.uk$',
                out, flags=re.UNICODE)
        self.assertTrue(m)
