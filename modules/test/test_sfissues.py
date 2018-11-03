"""
test_sfissues.py - tests for the sfissues module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from mock import MagicMock
from modules import sfissues
import web


class TestSFIssues(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_bugs(self):
        self.phenny.config.sf_issues_url = "https://sourceforge.net/p/apertium/news/feed.rss"
        self.input.nick = "bbc"
        sfissues.bugs(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("Basque-English 0.3.0 Released" in out)