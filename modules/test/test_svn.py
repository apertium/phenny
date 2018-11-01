"""
test_svn.py - tests for the svn poller module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from mock import MagicMock
from modules import svnpoller
import tools


class TestSVNPoller(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_esan_false(self):
        svnpoller.esan(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Sorry, there was nothing to report." in out)
