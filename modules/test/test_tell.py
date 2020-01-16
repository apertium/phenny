"""
Tests for phenny's tell.py
"""

import unittest
import datetime
from mock import MagicMock
from modules import tell, alias

class TestTell(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.host = 'irc.freenode.net'

        self.input = MagicMock()
        self.input2 = MagicMock()
        tell.setup(self.phenny)

    def create_alias(self, aliasName, input):
        self.input.group = lambda x: ['', 'add', aliasName][x]
        alias.alias(self.phenny, input)
        alias.aliasPairMerge(self.phenny, input.nick, aliasName)

    def create_reminder(self, teller):
        timenow = datetime.datetime.utcnow().strftime('%d %b %Y %H:%MZ')
        self.phenny.reminders[teller] = [(teller, 'do', timenow, 'something')]

    def test_messageAlert(self):
        self.input.sender = '#testsworth'
        self.input.nick = 'Testsworth'

        aliases = ['tester', 'testing', 'testmaster']
        self.phenny.reminders = {}

        for aliasName in aliases:
            self.create_alias(aliasName, self.input)
            self.create_reminder(aliasName)

        tell.messageAlert(self.phenny, self.input)

        text = ': You have messages. Say something, and I\'ll read them out.'
        self.phenny.say.assert_called_once_with(self.input.nick + text)

    def test_aliasGroupFor_multiple(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []

        aliases = ['tester', 'testing', 'testmaster']

        for aliasName in aliases:
            self.create_alias(aliasName, self.input)

        aliases.insert(0,'Testsworth')

        aligroup = alias.aliasGroupFor('Testsworth')
        self.assertTrue(aliases == aligroup)

    def test_aliasGroupFor_singleton(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []
        aliases = ['Testsworth']

        aligroup = alias.aliasGroupFor('Testsworth')
        self.assertTrue(aliases == aligroup)

    def test_aliasPairMerge(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []
        aliases = ['tester', 'testing', 'testmaster']
        for aliasName in aliases:
            self.create_alias(aliasName, self.input)

        self.input2.nick = 'Happy'
        aliases2 = ['joyful', 'ecstatic', 'euphoric', 'blissful']
        for aliasName in aliases2:
            self.create_alias(aliasName, self.input2)

        alias.aliasPairMerge(self.phenny, 'Testsworth', 'Happy')

        aliases.insert(0,'Testsworth')
        aliases2.insert(0,'Happy')
        joined = aliases + aliases2

        self.assertTrue(joined in alias.nick_aliases)

    def test_alias_noadded(self):
        self.input.nick = 'Testsworth'
        self.input.group = lambda x: ['alias', 'add', None][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Usage: .alias add <nick>')

    def test_alias_addself(self):
        self.input.nick = 'Testsworth'
        self.input.group = lambda x: ['alias', 'add', 'Testsworth'][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('I don\'t think that will be necessary.')

    def test_alias_alreadypaired(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = [['Testsworth', 'tests']]

        self.input.group = lambda x: ['alias', 'add', 'tests'][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('You and tests are already paired.')

    def test_alias_confirmreq(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []
        alias.nick_pairs.append(['tests', 'Testsworth'])

        self.input.group = lambda x: ['alias', 'add', 'tests'][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Confirmed alias request with tests. Your current aliases are: Testsworth, tests.')

    def test_alias_alreadysent(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []
        alias.nick_pairs.append(['Testsworth', 'tests'])

        self.input.group = lambda x: ['alias', 'add', 'tests'][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Alias request already exists. Switch your nick to tests and call \".alias add Testsworth\" to confirm.')

    def test_alias_valid(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []
        alias.nick_pairs = []

        self.input.group = lambda x: ['alias', 'add', 'tests'][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Alias request created. Switch your nick to tests and call \".alias add Testsworth\" to confirm.')

    def test_alias_listothers(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases.append(['happy', 'joyous'])
        self.input.group = lambda x: ['alias', 'list', 'happy'][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('happy\'s current aliases are: happy, joyous.')

    def test_alias_listself(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases.append(['Testsworth', 'tests'])
        self.input.group = lambda x: ['alias', 'list', None][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Your current aliases are: Testsworth, tests.')

    def test_alias_remove(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = [['Testsworth', 'tests']]
        self.input.group = lambda x: ['alias', 'remove'][x]

        alias.alias(self.phenny, self.input)
        self.assertTrue(alias.aliasGroupFor('Testsworth') == ['Testsworth'])
        self.phenny.reply.assert_called_once_with('You have removed Testsworth from its alias group')

    def test_alias_wrongcommand(self):
        self.input.group = lambda x: ['alias', 'eat'][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Usage: .alias add <nick>, .alias list <nick>?, .alias remove')

    def test_alias_noinput(self):
        self.input.group = lambda x: ['alias', None][x]

        alias.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with('Usage: .alias add <nick>, .alias list <nick>?, .alias remove')

    def test_fremind_toolong(self):
        self.input.nick = 'Testsworth'
        self.input.groups = lambda: ['testerrrrrrrrrrrrrrrrr', 'eat a cake']

        tell.f_remind(self.phenny, self.input, 'ask')
        self.phenny.reply.assert_called_once_with('That nickname is too long.')

    def test_fremind_tellself(self):
        self.input.nick = 'Testsworth'
        self.create_alias('tests', self.input)

        self.input.groups = lambda: ['tests', 'eat a cake']

        tell.f_remind(self.phenny, self.input, 'ask')
        self.phenny.say.assert_called_once_with('You can ask yourself that.')

    def test_fremind_valid(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []
        self.input.groups = lambda: ['tests', 'eat a cake']

        tell.f_remind(self.phenny, self.input, 'ask')
        responses = {'I\'ll pass that on when tests is around.', 'yeah, yeah', 'yeah, sure, whatever'}
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out in responses)

    def test_fremind_edgecase(self):
        self.input.nick = 'Testsworth'
        self.input.groups = lambda: ['me', 'eat a cake']

        tell.f_remind(self.phenny, self.input, 'ask')
        self.phenny.say.assert_called_once_with('Hey, I\'m not as stupid as Monty you know!')

    def test_ftell(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []
        self.input.groups = lambda: ['tests', 'eat a cake']

        tell.f_tell(self.phenny, self.input)
        responses = {'I\'ll pass that on when tests is around.', 'yeah, yeah', 'yeah, sure, whatever'}
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out in responses)

    def test_fask(self):
        self.input.nick = 'Testsworth'
        alias.nick_aliases = []
        self.input.groups = lambda: ['tests', 'eat a cake']

        tell.f_tell(self.phenny, self.input)
        responses = {'I\'ll pass that on when tests is around.', 'yeah, yeah', 'yeah, sure, whatever'}
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue(out in responses)

    def test_formatreminder(self):
        dt = datetime.datetime.utcnow().strftime('%d %b %Y %H:%MZ')
        ret = tell.formatReminder(['tests', 'ask', dt, 'to eat cake'], 'Testsworth', None)

        dt = dt[len(datetime.datetime.utcnow().strftime('%d %b')) + 1:]
        dt = dt.replace(datetime.datetime.utcnow().strftime('%Y '), '')
        self.assertTrue(ret == 'Testsworth: %s <tests> ask Testsworth to eat cake' % dt)
