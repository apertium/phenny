import unittest
from modules.test.command_test import CommandTest

class TestChoose(CommandTest, unittest.TestCase):
    modules = ['choose']

    def test_choose_strings(self):
        self.check_response('.choose canada usa', nick='bob',
                            expected=['bob: canada', 'bob: usa'])

    def test_choose_numerals(self):
        self.check_response('.choose 2 3', nick='bob',
                            expected=['bob: 2', 'bob: 3'])

    def test_choose_multiple(self):
        self.check_response('.choose dog cat hamster goldfish turtle',
                            nick='a',
                            expected=['a: dog', 'a: cat', 'a: hamster',
                                      'a: goldfish', 'a: turtle'])

    def test_choose_single(self):
        self.check_response('.choose haha', nick='blah',
                            expected='blah: haha')

    def test_choose_invalid(self):
        self.check_response(
            '.choose',
            '.choose <red> <blue> - for when you just can\'t decide')
