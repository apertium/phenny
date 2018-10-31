import unittest
from modules import sasl
from mock import MagicMock
 
class TestSasl(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.nick = 'tester'
 
    def test_irc_cap(self):
        d = {'LS':  ['multi-prefix', 'sasl', 'test'],
             'ACK': ['sasl', 'test'],
             'test':['test1']}
        for val in d:
            for b in d[val]:
                self.input.args[0] = b
                self.input.args[3] = val
                sasl.irc_cap(self.phenny, self.input)
                assert irc_cap_end()
 
    def test_irc_authenticated(self):
        d = {'Test':'TestPassword'}
        for val in d:
            self.phenny.config.nick = val
            self.phenny.config.password = d[val]
            sasl.irc_authenticated(self.phenny, self.input)
            assert irc_cap_end()
