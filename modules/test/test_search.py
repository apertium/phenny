"""
test_search.py - tests for the search module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock, patch
from modules import search
from web import catch_timeout, unquote


class TestSearch(unittest.TestCase):

    def setUp(self):
        self.engines = {
            'DuckDuckGo': 'https://api.duckduckgo.com',
            'Suggestion API': 'http://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q=test'
        }
        self.phenny = MagicMock()
        self.input = MagicMock()

    @patch('modules.search.requests.get')
    @catch_timeout
    def test_requests(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "AbstractText" : "TestText",
            "AbstractURL" : "https://testurl.com"
        }
        mock_get.return_value = mock_response
        self.input.group.return_value = 'test'
        search.search(self.phenny, self.input)
        self.phenny.say.assert_called_with('TestText - https://testurl.com')

    @catch_timeout
    def test_search(self):
        self.input.group.return_value = 'Apertium'
        search.search(self.phenny, self.input)
        self.assertTrue(self.phenny.say.called)

    @patch('modules.search.more')
    @catch_timeout
    def test_suggest(self, mock_more):
        self.input.group.return_value = 'test'
        search.suggest(self.phenny, self.input)
        self.assertTrue(mock_more.add_messages.called)
