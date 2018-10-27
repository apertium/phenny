import unittest
from mock import MagicMock
from modules import choose


class TestChoose(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_valid(self):
        self.input.group = lambda x: ['.choose', 'canada usa'][x]
        choose.choose(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out == 'canada' or out == 'usa')

    def test_valid2(self):
        self.input.group = lambda x: ['.choose', '2 3'][x]
        choose.choose(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out == '2' or out == '3')

    def test_valid3(self):
        self.input.group = lambda x: ['.choose', 'dog cat hamster goldfish turtle'][x]
        possibilities = ["dog", "cat", "hamster", "goldfish", "turtle"]
        choose.choose(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out in possibilities)

    def test_valid4(self):
        self.input.group = lambda x: ['.choose', 'haha'][x]
        choose.choose(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("haha")

    def test_invalid(self):
        self.input.group = lambda x: ['.choose', ''][x]
        choose.choose(self.phenny, self.input)
        self.phenny.say.assert_called_once_with(".choose <red> <blue> - for when you just can't decide")
