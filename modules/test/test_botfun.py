import unittest
from modules.test.command_test import CommandTest

class TestBotfun(CommandTest, unittest.TestCase):
    modules = ['botfun']

    def test_botfight(self):
        messages = {"hits ChanServ", "punches ChanServ", "kicks ChanServ", "hits ChanServ with a rubber hose",
                    "stabs ChanServ with a clean kitchen knife"}
        self.check_response('.botfight',
                            [f'\x01ACTION {x}\x01' for x in messages])

    def test_bothug(self):
        self.check_response('.bothug', '\x01ACTION hugs ChanServ\x01')
