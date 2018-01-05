"""
test_search.py - tests for the search module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock, patch
from modules.search import search, topics, suggest
from tools import is_up
from web import unquote


# tests involving Google searches are expected to fail because Google's Web
# Search API was officially deprecated in Nov. 2010 and discontinued in Sep.
# 2014; the eventual fix should use https://cse.google.com/cse/ and this hack:
# http://stackoverflow.com/a/11206266/1846915
#
# update as of 2017-01-14: this has been fixed
class TestSearch(unittest.TestCase):
    def setUp(self):
        self.skip_msg = '{:s} is down, skipping test.'
        self.engines = {
            'DuckDuckGo': 'https://api.duckduckgo.com',
            'Suggestion API': 'http://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q=test'
        }
        self.phenny = MagicMock()
        self.input = MagicMock()

    @patch('modules.search.requests.get')
    def test_requests(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "AbstractText" : "TestText",
            "AbstractURL" : "https://testurl.com"
        }
        mock_get.return_value = mock_response
        self.input.group.return_value = 'test'
        search(self.phenny, self.input)
        self.phenny.say.assert_called_with('TestText - https://testurl.com')

    def test_search(self):
        if not is_up(self.engines['DuckDuckGo']):
            self.skipTest(self.skip_msg.format('DuckDuckGo'))
        self.input.group.return_value = 'Apertium'
        search(self.phenny, self.input)
        self.assertTrue(self.phenny.say.called)

    @patch('modules.search.more')
    def test_suggest(self, mock_more):
        if not is_up(self.engines['Suggestion API']):
            self.skipTest(self.skip_msg.format('Suggestion API'))
        self.input.group.return_value = 'test'
        suggest(self.phenny, self.input)
        self.assertTrue(mock_more.add_messages.called)
