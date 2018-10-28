import unittest
from mock import MagicMock
from modules import apertiumchill

class TestApertiumchill(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.input.sender = "Testsworth"

    def test_chill_chill(self):
        apertiumchill.measure.channels["Testsworth"] = 20
        apertiumchill.chill(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("chill level is currently:" in out)

    def test_chill_notchill(self):
        apertiumchill.measure.channels["Testsworth"] = 0
        apertiumchill.chill(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("WARNING: CHILL LEVEL IS DANGEROUSLY LOW. RECOMMEND" in out)
