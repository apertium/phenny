import unittest
from mock import MagicMock
from modules import ethnologue as ethno


class TestEthnologue(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'

        self.input = MagicMock()
        self.input.nick = "tester"

    def test_shorten_num(self):
        self.assertTrue(ethno.shorten_num(994) == '994')
        self.assertTrue(ethno.shorten_num(99999348) == '100M')
        self.assertTrue(ethno.shorten_num(999348) == '999.3K')

    def test_write_ethnologue_codes(self):
        raw = MagicMock()
        raw.admin = True
        ethno.write_ethnologue_codes(self.phenny, raw=raw)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("Ethnologue iso-639 code fetch successful" in out)

    def test_ethnologue(self):
        self.input.group = lambda x: [None, "nld"][x]
        ethno.write_ethnologue_codes(self.phenny)
        ethno.ethnologue(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("Dutch" in out)

    def test_ethnologue_macrolanguage(self):
        self.input.group = lambda x: [None, "ara"][x]
        ethno.write_ethnologue_codes(self.phenny)
        ethno.ethnologue(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("macrolanguage" in out)

