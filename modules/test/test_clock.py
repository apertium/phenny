"""
test_clock.py - tests for the clock module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock, patch, call
from modules import clock
from web import catch_timeout


@patch('time.time')
class TestClock(unittest.TestCase):

    @catch_timeout
    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.host = 'irc.freenode.net'

        self.input = MagicMock()
        self.input.nick = 'Testsworth'

        clock.setup(self.phenny)

    @catch_timeout
    def test_time(self, mock_time):
        mock_time.return_value = 1338674651
        self.input.group.return_value = 'EDT'
        clock.f_time(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with(
            "Eastern Daylight Time: Sat, 02 Jun 2012 18:04:11", target=None)

    @catch_timeout
    def test_time_multi(self, mock_time):
        mock_time.return_value = 1338674651
        self.input.group.return_value = 'ACT'
        clock.f_time(self.phenny, self.input)
        msgs = [
            "Acre Time: Sat, 02 Jun 2012 17:04:11",
            "ASEAN Common Time: Sun, 03 Jun 2012 04:34:11",
            "ACT: Sun, 03 Jun 2012 08:04:11"
        ]
        self.phenny.reply.assert_called_once_with('; '.join(msgs), target=None)

    @catch_timeout
    def test_time_none(self, mock_time):
        mock_time.return_value = 1338674651
        self.input.group.return_value = 'FIZZ'
        clock.f_time(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with(
            "Sorry, I don't know about the 'FIZZ' timezone.")

    @catch_timeout
    def test_beats_zero(self, mock_time):
        mock_time.return_value = 0
        clock.beats(self.phenny, None)
        self.phenny.say.assert_called_with('@041')

    @catch_timeout
    def test_beats_normal(self, mock_time):
        mock_time.return_value = 369182
        clock.beats(self.phenny, None)
        self.phenny.say.assert_called_with('@314')

    @catch_timeout
    def test_yi_normal(self, mock_time):
        mock_time.return_value = 369182
        clock.yi(self.phenny, None)
        self.phenny.say.assert_called_with('Not yet...')

    @catch_timeout
    def test_yi_soon(self, mock_time):
        mock_time.return_value = 1339419000
        clock.yi(self.phenny, None)
        self.phenny.say.assert_called_with('Soon...')

    @catch_timeout
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

    def test_time_zone_convert_no_input(self, mock_time):
        clock.time_zone_convert(self.phenny, None)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Usage: .tz" in out)

    def test_time_zone_convert_invalid(self, mock_time):
        clock.time_zone_convert(self.phenny, "invalid")
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Usage: .tz" in out)
