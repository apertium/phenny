"""
test_codepoints.py - tests for the codepoints module
author: nu11us <work.willeggleston@gmail.com>
"""
import unittest
from mock import MagicMock
from modules import codepoints


class TestCodepoints(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_u_invalid(self):
        self.input.bytes = ""
        codepoints.u(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("You gave me zero length input." in out)

    def test_u_no_results(self):
        self.input.bytes = "randomtext"
        codepoints.u(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Sorry, no results" in out)

    def test_u_valid(self):
        self.input.bytes = " U+262D"
        codepoints.u(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("HAMMER AND SICKLE" in out)

    def test_u_space(self):
        self.input.bytes = "    "
        codepoints.u(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("1 SPACE (U+0020)" in out)

    def test_bytes(self):
        self.input.bytes = " \xe3"
        codepoints.bytes(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("ã" in out)

    def test_codepoint_extended(self):
        codepoint_list = list(codepoints.codepoint_extended("BBBB"))
        expected = "CJK UNIFIED IDEOGRAPH-2BBBB"
        status = False
        for i in codepoint_list:
            if expected in i:
                status = True
                break
        self.assertTrue(status)
