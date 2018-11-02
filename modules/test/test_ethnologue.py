import unittest
from mock import MagicMock
from modules import ethnologue

class TestEthnologue(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'

        self.input = MagicMock()
        self.input.nick = "tester"

    def test_shorten_num(self):
        self.assertTrue(ethnologue.shorten_num(994) == '994')
        self.assertTrue(ethnologue.shorten_num(99999348) == '100M')
        self.assertTrue(ethnologue.shorten_num(999348) == '999.3K')
