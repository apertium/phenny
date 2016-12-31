# -*- coding: utf-8 -*-
"""
test_tfw.py - tests for the fucking weather module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
import tools
from mock import MagicMock
from modules import tfw
from tools import is_up


class TestTfw(unittest.TestCase):
    def setUp(self):
        if not is_up('https://nominatim.openstreetmap.org'):
            self.skipTest('OpenStreetMap API is down, skipping test.')
        if not is_up('http://tgftp.nws.noaa.gov'):
            self.skipTest('NOAA weather data unavailable, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_badloc(self):
        self.input.group.return_value = 'tu3jgoajgoahghqog'
        tfw.tfw(self.phenny, self.input)
        self.phenny.say.assert_called_once_with(
            "WHERE THE FUCK IS THAT? Try another location.")

    def test_celsius(self):
        self.input.group.return_value = '24060'
        tfw.tfw(self.phenny, self.input, celsius=True)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^[\-\d]+°C‽ .* \- .* \- [A-Z]{4} \d{2}:\d{2}Z$', out,
                     flags=re.UNICODE)
        self.assertTrue(m)

    def test_fahrenheit(self):
        self.input.group.return_value = '24060'
        tfw.tfw(self.phenny, self.input, fahrenheit=True)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^[\-\d]+°F‽ .* \- .* \- [A-Z]{4} \d{2}:\d{2}Z$', out,
                     flags=re.UNICODE)
        self.assertTrue(m)

    def test_mev(self):
        self.input.group.return_value = '24060'
        tfw.tfwev(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^[\-\d\.]+ meV‽ .* \- .* \- [A-Z]{4} \d{2}:\d{2}Z$', out,
                     flags=re.UNICODE)
        self.assertTrue(m)

    def test_meter(self):
        self.input.group.return_value = '24060'
        tfw.tfw(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^[\-\d\.]+ Meters‽ .* \- .* \- [A-Z]{4} \d{2}:\d{2}Z$', out,
                     flags=re.UNICODE)
        self.assertTrue(m)

    def test_sexy_time(self):
        self.input.group.return_value = 'KBCB'
        tfw.web = MagicMock()
        tfw.metar.parse = lambda x: MagicMock(temperature=21)
        tfw.tfwf(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match(r'^69°F‽ IT\'S FUCKING SEXY TIME \- .*', out, flags=re.UNICODE)
        self.assertTrue(m)
