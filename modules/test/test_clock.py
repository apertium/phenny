"""
test_clock.py - tests for the clock module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from unittest.mock import patch
from modules.test.command_test import CommandTest
from web import catch_timeout


@patch('time.time')
class TestClock(CommandTest, unittest.TestCase):
    modules = ['clock']

    def test_time(self, mock_time):
        mock_time.return_value = 1338674651
        self.check_response('.time EDT',
                            "Eastern Daylight Time: Sat, 02 Jun 2012 18:04:11")

    def test_time_multi(self, mock_time):
        mock_time.return_value = 1338674651
        msgs = [
            "Acre Time: Sat, 02 Jun 2012 17:04:11",
            "ASEAN Common Time: Sun, 03 Jun 2012 06:04:11",
            "ACT: Sun, 03 Jun 2012 08:04:11"
        ]
        self.check_response('.time ACT', '; '.join(msgs))

    def test_time_none(self, mock_time):
        mock_time.return_value = 1338674651
        self.check_response('.time FIZZ',
                            "nick: Sorry, I don't know about the 'FIZZ' timezone.",
                            nick='nick')

    @catch_timeout
    def test_npl(self, mock_time):
        out = self.message_response('.npl')
        self.assertIn('- ntp1.npl.co.uk', out)

    def test_time_zone_convert_no_input(self, mock_time):
        out = self.message_response('.tz')
        self.assertIn("Usage: .tz", out)

    def test_time_zone_convert_invalid(self, mock_time):
        out = self.message_response('.tz invalid')
        self.assertIn("Usage: .tz", out)
