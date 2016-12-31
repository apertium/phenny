"""
test_remind.py - tests for the remind module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
import threading
import time
import tools
from mock import MagicMock, patch
from modules import remind


class TestRemind(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.host = 'test-phenny.example.com'

        remind.load_database = lambda name: {}
        remind.dump_database = lambda name, data: name
        remind.setup(self.phenny)

    def test_remind(self):
        secs = 5
        self.input.sender = '#testsworth'
        self.input.nick = 'Testsworth'
        self.input.bytes = '.in {0} seconds TEST REMIND'.format(secs)

        remind.remind(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Okay, will remind in {0}"
                " secs".format(secs))
        time.sleep(secs + 1)
        self.phenny.msg.assert_called_once_with(
            self.input.sender, self.input.nick + ': TEST REMIND')

    def test_remind_nomsg(self):
        secs = 5
        self.input.sender = '#testsworth'
        self.input.nick = 'Testsworth'
        self.input.bytes = '.in {0} seconds'.format(secs)

        remind.remind(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Okay, will remind in {0}"
                " secs".format(secs))
        time.sleep(secs + 1)
        self.phenny.msg.assert_called_once_with(self.input.sender, self.input.nick + '!')
