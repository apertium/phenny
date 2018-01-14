"""
test_urbandict.py - tests for the urban dictionary module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import urbandict
from web import catch_timeouts


@catch_timeouts
class TestUrbandict(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_result(self):
        word = 'slemp'
        self.input.group.return_value = word
        urbandict.urbandict(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - http://www\.urbandictionary\.com/define\.php\?term=.*$',
                     out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_none(self):
        word = '__no_word_here__'
        self.input.group.return_value = word
        urbandict.urbandict(self.phenny, self.input)
        self.phenny.say.assert_called_once_with('No results found for {0}'.format(word))
