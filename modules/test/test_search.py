"""
test_search.py - tests for the search module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules.search import google_ajax, google_search, google_count, \
        formatnumber, g, gc, gcs, bing_search, bing, duck_search, duck, \
        search, suggest
from tools import is_up


# tests involving Google searches are expected to fail because Google's Web
# Search API was officially deprecated in Nov. 2010 and discontinued in Sep.
# 2014; the eventual fix should use https://cse.google.com/cse/ and this hack:
# http://stackoverflow.com/a/11206266/1846915
class TestSearch(unittest.TestCase):
    def setUp(self):
        self.skip_msg = '{:s} is down, skipping test.'
        self.engines = {
            'Google': 'https://google.com',
            'Bing': 'https://bing.com',
            'DuckDuckGo': 'https://duckduckgo.com',
            'Suggestion script': 'http://websitedev.de'
        }
        self.phenny = MagicMock()
        self.input = MagicMock()

    @unittest.skip('see test_search.py')
    def test_google_ajax(self):
        if not is_up(self.engines['Google']):
            self.skipTest(self.skip_msg.format('Google'))
        data = google_ajax('phenny')
        self.assertIn('responseData', data)
        self.assertEqual(data['responseStatus'], 200)

    @unittest.skip('see test_search.py')
    def test_google_search(self):
        if not is_up(self.engines['Google']):
            self.skipTest(self.skip_msg.format('Google'))
        out = google_search('phenny')
        m = re.match('^https?://.*$', out, flags=re.UNICODE)
        self.assertTrue(m)

    @unittest.skip('see test_search.py')
    def test_g(self):
        if not is_up(self.engines['Google']):
            self.skipTest(self.skip_msg.format('Google'))
        self.input.group.return_value = 'swhack'
        g(self.phenny, self.input)
        self.phenny.reply.assert_not_called_with(
                "Problem getting data from Google.")

    @unittest.skip('see test_search.py')
    def test_gc(self):
        if not is_up(self.engines['Google']):
            self.skipTest(self.skip_msg.format('Google'))
        query = 'extrapolate'
        self.input.group.return_value = query
        gc(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^{0}: [0-9,\.]+$'.format(query), out, flags=re.UNICODE)
        self.assertTrue(m)

    @unittest.skip('see test_search.py')
    def test_gcs(self):
        if not is_up(self.engines['Google']):
            self.skipTest(self.skip_msg.format('Google'))
        self.input.group.return_value = 'vtluug virginia phenny'
        gcs(self.phenny, self.input)
        self.assertTrue(self.phenny.say.called)

    def test_bing_search(self):
        if not is_up(self.engines['Bing']):
            self.skipTest(self.skip_msg.format('Bing'))
        out = bing_search('phenny')
        m = re.match('^https?://.*$', out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_bing(self):
        if not is_up(self.engines['Bing']):
            self.skipTest(self.skip_msg.format('Bing'))
        self.input.group.return_value = 'swhack'
        bing(self.phenny, self.input)
        self.assertTrue(self.phenny.reply.called)

    def test_duck_search(self):
        if not is_up(self.engines['DuckDuckGo']):
            self.skipTest(self.skip_msg.format('DuckDuckGo'))
        out = duck_search('phenny')
        m = re.match('^https?://.*$', out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_duck(self):
        if not is_up(self.engines['DuckDuckGo']):
            self.skipTest(self.skip_msg.format('DuckDuckGo'))
        self.input.group.return_value = 'swhack'
        duck(self.phenny, self.input)
        self.assertTrue(self.phenny.reply.called)

    def test_search(self):
        if not (self.engines['DuckDuckGo'] or self.engines['Bing'] or self.engines['Google']):
            self.skipTest('All search engines are down, skipping test.')
        self.input.group.return_value = 'vtluug'
        duck(self.phenny, self.input)
        self.assertTrue(self.phenny.reply.called)

    def test_suggest(self):
        if not is_up(self.engines['Suggestion script']):
            self.skipTest(self.skip_msg.format('Suggestion script'))
        self.input.group.return_value = 'vtluug'
        suggest(self.phenny, self.input)
        self.assertTrue(self.phenny.reply.called or self.phenny.say.called)
