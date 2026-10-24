import unittest
from modules.test.command_test import CommandTest

class TestBotsnack(CommandTest, unittest.TestCase):
    modules = ['botsnack']

    def test_botsnack(self):
        self.message_response('.botsnack')

    def test_botslap(self):
        messages = {"hides in corner", "eats own hat", "apologises", "stares at feet", "points at zfe",
                    "didn't do anything", "doesn't deserve this", "hates you guys", "did it on purpose",
                    "is an inconsistent sketchy little bot", "scurries off"}
        self.check_response('.botslap',
                            [f'\x01ACTION {x}\x01' for x in messages])

    def test_increase(self):
        oldhunger = 12
        newhunger = self.get_module().increase_hunger(oldhunger, 5)
        self.assertTrue(oldhunger >= newhunger)

    def test_decrease(self):
        oldhunger = 12
        newhunger = self.get_module().decrease_hunger(oldhunger, 5)
        self.assertTrue(oldhunger <= newhunger)
