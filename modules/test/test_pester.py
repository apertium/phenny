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

        msg = "tester: I will start pestering testuser to study"
        self.phenny.say.assert_called_once_with(msg)

    def test_startpester2(self):
        self.input.group = lambda x: ['', 'testuser', 'to study'][x]

        pester.start_pester(self.phenny, self.input)

        msg = "tester: You are already pestering testuser"
        self.phenny.say.assert_called_once_with(msg)