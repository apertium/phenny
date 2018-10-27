import unittest
from mock import MagicMock
from modules import apertiumchill

class TestApertiumchill(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_chill(self):
        apertiumchill.chill(self.phenny, self.input)
        self.assertTrue(self.phenny.say.called)
