"""
Tests for phenny's tell.py
"""

import unittest
from mock import MagicMock, patch
from modules import tell


class TestTell(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.nick = 'phenny'

    def test_messageAlert(self):
        self.input.sender = '#testsworth'
        self.input.nick = 'Testsworth'

        tell.messageAlert(self.phenny, self.input)

        text = ': You have messages. Say something, and I\'ll read them out.'
        self.phenny.msg.assert_called_once_with(
            self.input.sender, self.input.nick + text)
