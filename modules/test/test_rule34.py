"""
test_rule34.py - tests for the rule 34 module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules.rule34 import rule34
from tools import is_up


class TestRule34(unittest.TestCase):
    def setUp(self):
        if not is_up('http://rule34.xxx'):
            self.skipTest('Rule34 website is down, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_result(self):
        self.input.group.return_value = 'python'
        rule34(self.phenny, self.input)

        out = self.phenny.reply.call_args[0][0]
        m = re.match('^!!NSFW!! -> http://rule34\.xxx/.* <- !!NSFW!!$', out,
                flags=re.UNICODE)
        self.assertTrue(m)
    def test_none(self):
        self.input.group.return_value = '__no_results_for_this__'
        rule34(self.phenny, self.input)

        self.phenny.reply.assert_called_once_with(
                "You just broke Rule 34! Better start uploading...")
