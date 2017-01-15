"""
test_mylife.py - tests for the mylife module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import mylife
from tools import is_up


class TestMylife(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    def test_fml(self):
        if not is_up('http://fmylife.com/random'):
            self.skipTest('FML website is down, skipping test.')
        mylife.fml(self.phenny, None)
        self.assertTrue(self.phenny.say.called)

    def test_mlia(self):
        if not is_up('http://mylifeisaverage.com'):
            self.skipTest('MLIA website is down, skipping test.')
        mylife.mlia(self.phenny, None)
        self.assertTrue(self.phenny.say.called)
