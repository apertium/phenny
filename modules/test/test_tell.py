"""
Tests for phenny's tell.py
"""

import unittest
import datetime
from modules.test.command_test import CommandTest

class TestTell(CommandTest, unittest.TestCase):
    modules = ['tell']

    def create_reminder(self, teller):
        timenow = datetime.datetime.now(datetime.UTC).strftime('%d %b %Y %H:%MZ')
        self.phenny.reminders[teller] = [(teller, 'do', timenow, 'something')]

    def test_messageAlert(self):
        self.create_reminder('Testsworth')
        out = self.run_event(':Testsworth!blah@blah JOIN #testsworth')
        self.assertEqual(out, ['PRIVMSG #testsworth :Testsworth: You have messages. Say something, and I\'ll read them out.'])

    def test_fremind_valid(self):
        self.check_response(
            'begiak-test: ask tests eat a cake', nick='Testsworth',
            expected=['Testsworth: I\'ll pass that on when tests is around.', 'Testsworth: yeah, yeah', 'Testsworth: yeah, sure, whatever'])

    def test_fremind_edgecase(self):
        self.check_response('begiak-test: ask me eat a cake',
                            expected='Hey, I\'m not as stupid as Monty you know!')

    def test_ftell(self):
        responses = ['Testsworth: I\'ll pass that on when tests is around.', 'Testsworth: yeah, yeah', 'Testsworth: yeah, sure, whatever']
        self.check_response(
            '.tell tests eat a cake', nick='Testsworth',
            expected=responses)

    def test_formatreminder(self):
        dt = datetime.datetime.now(datetime.UTC).strftime('%d %b %Y %H:%MZ')
        ret = self.get_module().formatReminder(['tests', 'ask', dt, 'to eat cake'], 'Testsworth', None)

        dt = dt[len(datetime.datetime.now(datetime.UTC).strftime('%d %b')) + 1:]
        dt = dt.replace(datetime.datetime.now(datetime.UTC).strftime('%Y '), '')
        self.assertEqual(ret, 'Testsworth: %s <tests> ask Testsworth to eat cake' % dt)
