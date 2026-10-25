"""
test_search.py - tests for the search module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from unittest.mock import patch
from modules.test.command_test import CommandTest

@patch('web.is_up', return_value=True)
@patch('web.api_call')
class TestSearch(CommandTest, unittest.TestCase):
    modules = ['search']

    def test_requests(self, mock_api, mock_up):
        mock_api.return_value = {
            "AbstractText" : "TestText",
            "AbstractURL" : "https://testurl.com"
        }
        self.check_response('.search test',
                            'TestText - https://testurl.com')

    def test_search(self, mock_api, mock_up):
        mock_api.return_value = {}
        out = self.run_message('.search Apertium')
        self.assertTrue(out)

    def test_suggest(self, mock_api, mock_up):
        mock_api.return_value = [[], ['hi', 'hi']]
        out = self.run_message('.suggest test')
        self.assertTrue(out)
