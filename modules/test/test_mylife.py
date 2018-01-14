"""
test_mylife.py - tests for the mylife module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import mylife
from web import catch_timeouts


@catch_timeouts
class TestMylife(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    def test_fml(self):
        mylife.fml(self.phenny, None)
        self.assertTrue(self.phenny.say.called)

    def test_mlia(self):
        mylife.mlia(self.phenny, None)
        self.assertTrue(self.phenny.say.called)
