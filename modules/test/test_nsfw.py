"""
test_nsfw.py - some things just aren't safe for work, the test cases
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules.nsfw import nsfw


class TestNsfw(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_nsfw(self):
        self.input.group.return_value = "test"
        nsfw(self.phenny, self.input)
        self.phenny.say.assert_called_once_with(
            "!!NSFW!! -> test <- !!NSFW!!")

    def test_nsfw_none(self):
        self.input.group.return_value = None
        nsfw(self.phenny, self.input)
        self.phenny.say.assert_called_once_with(
            ".nsfw <link> - for when a link isn't safe for work")
