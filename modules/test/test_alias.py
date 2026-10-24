"""
Tests for phenny's alias.py
"""

import unittest
from modules.test.command_test import CommandTest

class TestAlias(CommandTest, unittest.TestCase):
    modules = ['alias']

    def set_context(self, nick_aliases=None, nick_pairs=None):
        self.get_module().nick_aliases = nick_aliases or []
        self.get_module().nick_pairs = nick_pairs or []

    def create_alias(self, nick, other):
        self.message_response('.alias add '+other, nick=nick)
        self.get_module().aliasPairMerge(self.phenny, nick, other)

    def test_aliasGroupFor_multiple(self):
        self.set_context([])

        aliases = ['tester', 'testing', 'testmaster']

        for aliasName in aliases:
            self.create_alias(aliasName, 'Testsworth')

        aliases.insert(0,'Testsworth')

        aligroup = self.get_module().aliasGroupFor('Testsworth')
        self.assertEqual(sorted(aliases), sorted(aligroup))

    def test_aliasGroupFor_singleton(self):
        self.set_context([])
        aliases = ['Testsworth']

        aligroup = self.get_module().aliasGroupFor('Testsworth')
        self.assertEqual(aliases, aligroup)

    def test_aliasPairMerge(self):
        self.set_context([])
        aliases = ['tester', 'testing', 'testmaster']
        for aliasName in aliases:
            self.create_alias(aliasName, 'Testsworth')

        aliases2 = ['joyful', 'ecstatic', 'euphoric', 'blissful']
        for aliasName in aliases2:
            self.create_alias(aliasName, 'Happy')

        self.get_module().aliasPairMerge(self.phenny, 'Testsworth', 'Happy')

        aliases.insert(0,'Testsworth')
        aliases2.insert(0,'Happy')
        joined = aliases + aliases2

        self.assertEqual(sorted(joined), sorted(self.get_module().nick_aliases[0]))

    def test_alias_noadded(self):
        self.check_response(
            '.alias add', nick='Testsworth',
            expected='Testsworth: Usage: .alias add <nick>')

    def test_alias_addself(self):
        self.check_response(
            '.alias add Testsworth', nick='Testsworth',
            expected='Testsworth: I don\'t think that will be necessary.')

    def test_alias_alreadypaired(self):
        self.set_context([['Testsworth', 'tests']])
        self.check_response(
            '.alias add tests', nick='Testsworth',
            expected='Testsworth: You and tests are already paired.')

    def test_alias_confirmreq(self):
        self.set_context([], [['tests', 'Testsworth']])
        self.check_response(
            '.alias add tests', nick='Testsworth',
            expected='Testsworth: Confirmed alias request with tests. Your current aliases are: Testsworth, tests.')

    def test_alias_alreadysent(self):
        self.set_context([], [['Testsworth', 'tests']])
        self.check_response(
            '.alias add tests', nick='Testsworth',
            expected='Testsworth: Alias request already exists. Switch your nick to tests and call \".alias add Testsworth\" to confirm.')

    def test_alias_valid(self):
        self.set_context([], [])
        self.check_response(
            '.alias add tests', nick='Testsworth',
            expected='Testsworth: Alias request created. Switch your nick to tests and call \".alias add Testsworth\" to confirm.')

    def test_alias_listothers(self):
        self.set_context([['happy', 'joyous']])
        self.check_response(
            '.alias list happy', nick='Testsworth',
            expected='Testsworth: happy\'s current aliases are: happy, joyous.')

    def test_alias_listself(self):
        self.set_context([['Testsworth', 'tests']])
        out = self.message_response('.alias list', nick='Testsworth')
        self.assertEqual(out, 'Testsworth: Your current aliases are: Testsworth, tests.')

    def test_alias_remove(self):
        self.set_context([['Testsworth', 'tests']])
        out = self.message_response('.alias remove', nick='Testsworth')
        self.assertEqual(self.get_module().aliasGroupFor('Testsworth'), ['Testsworth'])
        self.assertEqual(out, 'Testsworth: You have removed Testsworth from its alias group')

    def test_alias_wrongcommand(self):
        self.check_response(
            '.alias eat', nick='bob',
            expected='bob: Usage: .alias add <nick>, .alias list <nick>?, .alias remove')

    def test_alias_noinput(self):
        self.check_response(
            '.alias', nick='bob',
            expected='bob: Usage: .alias add <nick>, .alias list <nick>?, .alias remove')
