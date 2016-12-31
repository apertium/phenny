"""
test_wuvt.py - tests for the wuvt module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules.wuvt import wuvt
from tools import is_up


class TestWuvt(unittest.TestCase):
    def setUp(self):
        if not is_up('https://www.wuvt.vt.edu'):
            self.skipTest('WUVT data is not available, skipping test.')
        self.phenny = MagicMock()

    def test_wuvt(self):
        wuvt(self.phenny, None)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* is currently playing .* by .*$', out,
                flags=re.UNICODE)
        self.assertTrue(m)
