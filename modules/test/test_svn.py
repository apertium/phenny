"""
test_svn.py - tests for the svn poller module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from modules.test.command_test import CommandTest

class TestSVNPoller(CommandTest, unittest.TestCase):
    modules = ['svnpoller']

    def add_config(self):
        self.config.svn_repositories = []

    def test_esan_false(self):
        out = self.run_message('.esan', nick='joe', channel='#ch')
        self.assertEqual(out, ["PRIVMSG #ch :joe: Hold on a second, I'm polling!",
                               'PRIVMSG #ch :joe: Sorry, there was nothing to report.'])
