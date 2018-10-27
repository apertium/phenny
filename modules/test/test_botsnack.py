import unittest
import random
from mock import MagicMock
from modules import botsnack


class TestBotsnack(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_botsnack(self):
        botsnack.botsnack(self.phenny, self.input)
        self.assertTrue(self.phenny.say.called or self.phenny.do.called)

    def test_botslap(self):
        botsnack.botslap(self.phenny, self.input)
        messages = ["hides in corner", "eats own hat", "apologises", "stares at feet", "points at zfe",
                    "didn't do anything", "doesn't deserve this", "hates you guys", "did it on purpose",
                    "is an inconsistent sketchy little bot", "scurries off"]
        out = self.phenny.do.call_args[0][0]
        self.assertTrue(out in messages)

    def test_increase(self):
        oldhunger = random.randint(0,100)
        newhunger = botsnack.increase_hunger(oldhunger, 5)
        self.assertTrue(oldhunger >= newhunger)

    def test_decrease(self):
        oldhunger = random.randint(0, 100)
        newhunger = botsnack.decrease_hunger(oldhunger, 5)
        self.assertTrue(oldhunger <= newhunger)
