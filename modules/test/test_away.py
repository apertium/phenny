import unittest
from mock import MagicMock, Mock
from modules import away

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.input.count.return_value = 0 # Mock Attribute to provide the messages
        self.input.nick = 'Testseen'
        
    def testWhereIs(self):
        self.input = "whereis Testwhereis"
        away.whereis(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Sorry, Testwhereis seems to be AWOL...')

    def testAway(self):
        away.away(self.phenny, self.input)
        self.input = "whereis Testseen"
        away.whereis(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Testseen said: I'm away right now")

    def testBack(self):
        away.back(self.phenny, self.input)
        self.input = "whereis Testseen"
        away.whereis(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Testseen said: I'm around at the minute")

    def testAwayBack(self):
        away.away(self.phenny, self.input)
        away.back(self.phenny, self.input)
        self.input = "whereis Testseen"
        away.whereis(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Testseen said: I'm around at the minute")

    def testBackAway(self):
        away.back(self.phenny, self.input)
        away.away(self.phenny, self.input)
        self.input = "whereis Testseen"
        away.whereis(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Testseen said: I'm away right now")
