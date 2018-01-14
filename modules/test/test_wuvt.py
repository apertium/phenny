"""
test_wuvt.py - tests for the wuvt module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import wuvt
from web import catch_timeouts


@catch_timeouts
class TestWuvt(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()

    def test_wuvt(self):
        wuvt.wuvt(self.phenny, None)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* is currently playing .* by .*$', out,
                flags=re.UNICODE)
        self.assertTrue(m)
