import unittest
from modules.test.command_test import CommandTest

class TestPester(CommandTest, unittest.TestCase):
    modules = ['pester']

    def test_startpester(self):
        self.check_response(
            '.pester testuser to study', nick='tester',
            expected='tester: I will start pestering testuser to study')
