"""
test_commit.py - tests for the what the commit module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import commit
from web import catch_timeout


class TestCommit(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    @catch_timeout
    def test_commit(self):
        commit.commit(self.phenny, None)
        self.assertTrue(self.phenny.reply.called)
