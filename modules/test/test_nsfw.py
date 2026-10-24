"""
test_nsfw.py - some things just aren't safe for work, the test cases
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from modules.test.command_test import CommandTest

class TestNsfw(CommandTest, unittest.TestCase):
    modules = ['nsfw']

    def test_nsfw(self):
        self.check_response('.nsfw test',
                            expected='!!NSFW!! -> test <- !!NSFW!!')

    def test_nsfw_none(self):
        self.check_response(
            '.nsfw',
            expected=".nsfw <link> - for when a link isn't safe for work")
