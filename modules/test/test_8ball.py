import unittest
from mock import MagicMock, Mock
from modules import eightball

class TestEightBall(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def testEightBall(self):
        eightball.eightball(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out in eightball.QUOTES)
