"""
test_slogan.py - tests for the slogan module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules.slogan import sloganize, slogan
from tools import is_up


class TestSlogan(unittest.TestCase):
    def setUp(self):
        if not is_up('http://www.sloganizer.net'):
            self.skipTest('Sloganizer server is down, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_sloganize(self):
        out = sloganize('slogan')
        self.assertRegex(out, ".*slogan.*")

    def test_slogan(self):
        self.input.group.return_value = 'slogan'
        slogan(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertRegex(out, ".*slogan.*")

    def test_slogan_none(self):
        self.input.group.return_value = None
        slogan(self.phenny, self.input)
        self.phenny.say.assert_called_once_with(
            "You need to specify a word; try .slogan Granola")
