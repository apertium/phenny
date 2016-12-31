"""
test_fcc.py - tests for the fcc callsign lookup module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules.fcc import fcc
from tools import is_up


class TestFcc(unittest.TestCase):
    def setUp(self):
        if not is_up('http://callook.info'):
            self.skipTest('FCC database server is down, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_result(self):
        callsign = 'KK4EWT'
        ham = 'JAMES B WILLIAMS'
        key = 3326562
        self.input.group.return_value = callsign
        fcc(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('{0} - {1} - '
            'http://wireless2.fcc.gov/UlsApp/UlsSearch/license.jsp?licKey={2}'
            .format(callsign, ham, key))

    def test_none(self):
        callsign = 'XFOOBAR'
        self.input.group.return_value = callsign
        fcc(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('No results found for {0}'.format(callsign))
