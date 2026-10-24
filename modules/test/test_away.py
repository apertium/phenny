import unittest
from modules.test.command_test import CommandTest

class TestQueue(CommandTest, unittest.TestCase):
    modules = ['away']

    def testWhereIs(self):
        self.check_response(
            '.whereis Testwhereis', nick='blah',
            expected='blah: Sorry, Testwhereis seems to be AWOL...')

    def testAway(self):
        self.run_message('.away', nick='Testseen')
        self.check_response('.whereis Testseen', nick='test',
                            expected="test: Testseen said: I'm away right now")

    def testBack(self):
        self.run_message('.back', nick='Testseen')
        self.check_response('.whereis Testseen', nick='test',
                            expected="test: Testseen said: I'm around at the minute")

    def testAwayBack(self):
        self.run_message('.away', nick='Testseen')
        self.run_message('.back', nick='Testseen')
        self.check_response('.whereis Testseen', nick='test',
                            expected="test: Testseen said: I'm around at the minute")

    def testBackAway(self):
        self.run_message('.back', nick='Testseen')
        self.run_message('.away', nick='Testseen')
        self.check_response('.whereis Testseen', nick='test',
                            expected="test: Testseen said: I'm away right now")
