import unittest
from mock import MagicMock
from modules import pester

class TestPester(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'

        self.input = MagicMock()
        self.input.nick = "tester"
        pester.setup(self.phenny)

    def test_startpester(self):
        self.input.group = lambda x: ['', 'testuser', 'to study'][x]

        pester.start_pester(self.phenny, self.input)

        self.phenny.say.assert_called_once_with("tester: I will start pestering testuser to study")
