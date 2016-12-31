"""
test_commit.py - tests for the what the commit module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules.commit import commit
from tools import is_up


class TestCommit(unittest.TestCase):
    def setUp(self):
        if not is_up('http://whatthecommit.com'):
            self.skipTest('\'What the Commit\' server is down, skipping test.')
        self.phenny = MagicMock()

    def test_commit(self):
        commit(self.phenny, None)
        self.assertTrue(self.phenny.reply.called)
