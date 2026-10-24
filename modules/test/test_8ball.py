import unittest
from modules import eightball
from modules.test.command_test import CommandTest

class TestEightBall(CommandTest, unittest.TestCase):
    modules = ['eightball']

    def testEightBall(self):
        out = self.message_response('.8ball are you there?')
        self.assertIn(': ', out)
        self.assertIn(out.split(': ', 1)[1], eightball.QUOTES)
