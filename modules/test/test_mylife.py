"""
test_mylife.py - tests for the mylife module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import mylife
from web import catch_timeout


class TestMylife(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    @catch_timeout
    def test_fml(self):
        mylife.fml(self.phenny, None)
        self.assertTrue(self.phenny.say.called)

    @catch_timeout
    def test_mlia(self):
        mylife.mlia(self.phenny, None)
        self.assertTrue(self.phenny.say.called)
