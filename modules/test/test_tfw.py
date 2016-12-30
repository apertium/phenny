# -*- coding: utf-8 -*-
"""
test_tfw.py - tests for the fucking weather module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import re
import unittest
import tools
import requests
from mock import MagicMock, Mock
from modules import tfw


class TestTfw(unittest.TestCase):
    def setUp(self):
        try:
            requests.get('https://nominatim.openstreetmap.org').raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            self.skipTest('OpenStreetMap API is down, skipping test.')
        try:
            requests.get('http://tgftp.nws.noaa.gov').raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            self.skipTest('NOAA weather data unavailable, skipping test.')
        self.phenny = MagicMock()

    def test_badloc(self):
        input = Mock(group=lambda x: 'tu3jgoajgoahghqog')
        tfw.tfw(self.phenny, input)

        self.phenny.say.assert_called_once_with(
            "WHERE THE FUCK IS THAT? Try another location.")

    def test_celsius(self):
        input = Mock(group=lambda x: '24060')
        tfw.tfw(self.phenny, input, celsius=True)

        out = self.phenny.say.call_args[0][0]
        m = re.match('^[\-\d]+°C‽ .* \- .* \- [A-Z]{4} \d{2}:\d{2}Z$', out,
                     flags=re.UNICODE)
        self.assertTrue(m)

    def test_fahrenheit(self):
        input = Mock(group=lambda x: '24060')
        tfw.tfw(self.phenny, input, fahrenheit=True)

        out = self.phenny.say.call_args[0][0]
        m = re.match('^[\-\d]+°F‽ .* \- .* \- [A-Z]{4} \d{2}:\d{2}Z$', out,
                     flags=re.UNICODE)
        self.assertTrue(m)

    def test_mev(self):
        input = Mock(group=lambda x: '24060')
        tfw.tfwev(self.phenny, input)

        out = self.phenny.say.call_args[0][0]
        m = re.match('^[\-\d\.]+ meV‽ .* \- .* \- [A-Z]{4} \d{2}:\d{2}Z$', out,
                     flags=re.UNICODE)
        self.assertTrue(m)

    def test_meter(self):
        input = Mock(group=lambda x: '24060')
        tfw.tfw(self.phenny, input)

        out = self.phenny.say.call_args[0][0]
        m = re.match('^[\-\d\.]+ Meters‽ .* \- .* \- [A-Z]{4} \d{2}:\d{2}Z$', out,
                     flags=re.UNICODE)
        self.assertTrue(m)

    def test_sexy_time(self):
        input = Mock(group=lambda x: 'KBCB')
        tfw.web = MagicMock()
        tfw.metar.parse = lambda x: Mock(temperature=21)
        tfw.tfwf(self.phenny, input)

        out = self.phenny.say.call_args[0][0]
        m = re.match(
            r'^69°F‽ IT\'S FUCKING SEXY TIME \- .*',
            out,
            flags=re.UNICODE)
        self.assertTrue(m)
