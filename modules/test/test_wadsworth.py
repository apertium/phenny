"""
test_wadsworth.py - the wadsworth.py module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules.wadsworth import wadsworth


class TestWadsworth(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_wadsworth(self):
        self.input.group.return_value = "Apply Wadsworth's Constant to a string"
        wadsworth(self.phenny, self.input)

        self.phenny.say.assert_called_once_with(
                "Constant to a string")
