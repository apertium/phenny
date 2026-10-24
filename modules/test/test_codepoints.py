"""
test_codepoints.py - tests for the codepoints module
author: nu11us <work.willeggleston@gmail.com>
"""
import unittest
from modules.test.command_test import CommandTest

class TestCodepoints(CommandTest, unittest.TestCase):
    modules = ['codepoints']

    def test_u_invalid(self):
        out = self.message_response('.u ')
        self.assertIn("You gave me zero length input.", out)

    def test_u_no_results(self):
        out = self.message_response('.u randomtext')
        self.assertIn("Sorry, no results", out)

    def test_u_valid(self):
        out = self.message_response('.u \u262D')
        self.assertIn("HAMMER AND SICKLE", out)

    def test_bytes(self):
        out = self.message_response('.u \xe3')
        self.assertIn("ã", out)

    def test_codepoint_extended(self):
        codepoint_list = list(self.get_module().codepoint_extended("BBBB"))
        expected = "CJK UNIFIED IDEOGRAPH-2BBBB"
        status = False
        for i in codepoint_list:
            if expected in i:
                status = True
                break
        self.assertTrue(status)
