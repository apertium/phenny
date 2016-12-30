"""
test_search.py - tests for the search module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import re
import unittest
from mock import MagicMock, Mock
from modules.search import google_ajax, google_search, google_count, \
        formatnumber, g, gc, gcs, bing_search, bing, duck_search, duck, \
        search, suggest

# tests involving Google searches are expected failures because Google's Web
# Search API was officially deprecated in Nov. 2010 and discontinued in Sep.
# 2014; the eventual fix should use https://cse.google.com/cse/ and this hack:
# http://stackoverflow.com/a/11206266/1846915
class TestSearch(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    @unittest.expectedFailure
    def test_google_ajax(self):
        data = google_ajax('phenny')
        self.assertIn('responseData', data)
        self.assertEqual(data['responseStatus'], 200)

    @unittest.expectedFailure
    def test_google_search(self):
        out = google_search('phenny')
        m = re.match('^https?://.*$', out, flags=re.UNICODE)
        self.assertTrue(m)

    @unittest.expectedFailure
    def test_g(self):
        input = Mock(group=lambda x: 'swhack')
        g(self.phenny, input)
        self.phenny.reply.assert_not_called_with(
                "Problem getting data from Google.")

    @unittest.expectedFailure
    def test_gc(self):
        query = 'extrapolate'
        input = Mock(group=lambda x: query)
        gc(self.phenny, input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^{0}: [0-9,\.]+$'.format(query), out, flags=re.UNICODE)
        self.assertTrue(m)

    @unittest.expectedFailure
    def test_gcs(self):
        input = Mock(group=lambda x: 'vtluug virginia phenny')
        gcs(self.phenny, input)
        self.assertTrue(self.phenny.say.called)

    def test_bing_search(self):
        out = bing_search('phenny')
        m = re.match('^https?://.*$', out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_bing(self):
        input = Mock(group=lambda x: 'swhack')
        bing(self.phenny, input)
        self.assertTrue(self.phenny.reply.called)

    def test_duck_search(self):
        out = duck_search('phenny')
        m = re.match('^https?://.*$', out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_duck(self):
        input = Mock(group=lambda x: 'swhack')
        duck(self.phenny, input)
        self.assertTrue(self.phenny.reply.called)

    def test_search(self):
        input = Mock(group=lambda x: 'vtluug')
        duck(self.phenny, input)
        self.assertTrue(self.phenny.reply.called)

    def test_suggest(self):
        input = Mock(group=lambda x: 'vtluug')
        suggest(self.phenny, input)
        self.assertTrue(self.phenny.reply.called or self.phenny.say.called)
