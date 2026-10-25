# -*- coding: utf-8 -*-
"""
test_wiktionary.py - tests for the wiktionary module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from modules.test.command_test import CommandTest
from web import catch_timeout

class TestWiktionary(CommandTest, unittest.TestCase):
    modules = ['wiktionary']

    @catch_timeout
    def test_wiktionary(self):
        w = self.get_module().wiktionary(self.phenny, 'test')
        self.assertTrue(len(w[1]) > 0)

    @catch_timeout
    def test_wiktionary_none(self):
        w = self.get_module().wiktionary(self.phenny, 'Hell!')
        self.assertEqual(len(w[0]), 0)
        self.assertEqual(len(w[1]), 0)

    @catch_timeout
    def test_w(self):
        out = self.message_response('.w test')
        self.assertIn('test — noun: ', out)

    @catch_timeout
    def test_w_none(self):
        out = self.run_message('.w boook')
        self.assertEqual(len(out), 2)
        self.assertIn('Perhaps you meant \'book\'?', out[0])
        self.assertIn('book — noun:', out[1])

        self.check_response('.w vnuericjnrfu',
                            "Couldn't find any definitions for vnuericjnrfu.")
