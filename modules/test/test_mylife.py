"""
test_mylife.py - tests for the mylife module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import unittest
import requests
from mock import MagicMock
from modules import mylife


class TestMylife(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    def test_fml(self):
        try:
            requests.get('http://fmylife.com').raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            self.skipTest('FML website is down, skipping test.')
        mylife.fml(self.phenny, None)
        self.assertTrue(self.phenny.say.called)

    def test_mlia(self):
        try:
            requests.get('http://mylifeisaverage.com').raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            self.skipTest('MLIA website is down, skipping test.')
        mylife.mlia(self.phenny, None)
        self.assertTrue(self.phenny.say.called)
