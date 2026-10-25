"""
test_sfissues.py - tests for the sfissues module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from modules.test.command_test import CommandTest

class TestSFIssues(CommandTest, unittest.TestCase):
    modules = ['sfissues']

    def test_bugs(self):
        self.phenny.config.sf_issues_url = "https://sourceforge.net/p/apertium/news/feed.rss"
        self.phenny.nick = 'begiak'
        out = self.message_response('begiak: bugs!')
        self.assertTrue("Basque-English 0.3.0 Released" in out)
