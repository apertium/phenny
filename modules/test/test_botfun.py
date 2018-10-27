import unittest
from mock import MagicMock
from modules import botfun


class TestBotfun(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_botfight(self):
        messages = ["hits ChanServ", "punches ChanServ", "kicks ChanServ", "hits ChanServ with a rubber hose",
                    "stabs ChanServ with a clean kitchen knife"]
        botfun.botfight(self.phenny, self.input)
        out = self.phenny.do.call_args[0][0]
        self.assertTrue(out in messages)

    def test_bothug(self):
        botfun.bothug(self.phenny, self.input)
        self.phenny.say.assert_called_once_with("hugs ChanServ")
