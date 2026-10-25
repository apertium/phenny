"""
test_remind.py - tests for the remind module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import unittest
from modules.test.command_test import CommandTest
import time

class TestRemind(CommandTest, unittest.TestCase):
    modules = ['remind']

    def test_remind(self):
        secs = 5
        self.check_response(f'.in {secs} seconds TEST REMIND',
                            nick='Testsworth', channel='#testsworth',
                            expected=f'Testsworth: Okay, will remind in {secs} secs')
        time.sleep(secs + 1)
        self.assertEqual(self.phenny.write_queue,
                         ['PRIVMSG #testsworth :Testsworth: TEST REMIND'])

    def test_remind_nomsg(self):
        secs = 5
        self.check_response(f'.in {secs} seconds',
                            nick='Testsworth', channel='#testsworth',
                            expected=f'Testsworth: Okay, will remind in {secs} secs')
        time.sleep(secs + 1)
        self.assertEqual(self.phenny.write_queue,
                         ['PRIVMSG #testsworth :Testsworth!'])
