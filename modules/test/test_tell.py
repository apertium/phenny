"""
Tests for phenny's tell.py
"""

import unittest
import datetime
from mock import MagicMock
from modules import tell

class TestTell(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.host = 'irc.freenode.net'

        self.input = MagicMock()
        self.input2 = MagicMock()
        tell.setup(self.phenny)

    def create_alias(self, alias, input):
        self.input.group = lambda x: ['', 'add', alias][x]
        tell.alias(self.phenny, input)
        tell.aliasPairMerge(self.phenny, input.nick, alias)

    def create_reminder(self, teller):
        timenow = datetime.datetime.utcnow().strftime('%d %b %Y %H:%MZ')
        self.phenny.reminders[teller] = [(teller, 'do', timenow, 'something')]

    def test_messageAlert(self):
        self.input.sender = '#testsworth'
        self.input.nick = 'Testsworth'

        aliases = ['tester', 'testing', 'testmaster']
        self.phenny.reminders = {}

        for alias in aliases:
            self.create_alias(alias, self.input)
            self.create_reminder(alias)

        tell.messageAlert(self.phenny, self.input)

        text = ': You have messages. Say something, and I\'ll read them out.'
        self.phenny.say.assert_called_once_with(self.input.nick + text)

    def test_aliasGroupFor(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases = []

        aliases = ['tester', 'testing', 'testmaster']

        for alias in aliases:
            self.create_alias(alias, self.input)

        aliases.insert(0,'Testsworth')

        aligroup = tell.aliasGroupFor('Testsworth')
        self.assertTrue(aliases == aligroup)

    def test_aliasGroupFor2(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases = []
        aliases = ['Testsworth']

        aligroup = tell.aliasGroupFor('Testsworth')
        self.assertTrue(aliases == aligroup)

    def test_aliasPairMerge(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases = []
        aliases = ['tester', 'testing', 'testmaster']
        for alias in aliases:
            self.create_alias(alias, self.input)

        self.input2.nick = 'Happy'
        aliases2 = ['joyful', 'ecstatic', 'euphoric', 'blissful']
        for alias in aliases2:
            self.create_alias(alias, self.input2)

        tell.aliasPairMerge(self.phenny, 'Testsworth', 'Happy')

        aliases.insert(0,'Testsworth')
        aliases2.insert(0,'Happy')
        joined = aliases + aliases2

        self.assertTrue(joined in tell.nick_aliases)

    def test_alias(self):
        self.input.nick = 'Testsworth'
        self.input.group = lambda x: ['', 'add', None][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Usage: .alias add <nick>")

    def test_alias2(self):
        self.input.nick = 'Testsworth'
        self.input.group = lambda x: ['', 'add', 'Testsworth'][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("I don't think that will be necessary.")

    def test_alias3(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases.append(['Testsworth', 'tests'])

        self.input.group = lambda x: ['', 'add', 'tests'][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("You and tests are already paired.")

    def test_alias4(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases = []
        tell.nick_pairs.append(['tests', 'Testsworth'])

        self.input.group = lambda x: ['', 'add', 'tests'][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Confirmed alias request with tests. Your current aliases are: Testsworth, tests.")

    def test_alias5(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases = []
        tell.nick_pairs.append(['Testsworth', 'tests'])

        self.input.group = lambda x: ['', 'add', 'tests'][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Alias request already exists. Switch your nick to tests and call \".alias add Testsworth\" to confirm.")

    def test_alias6(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases = []

        self.input.group = lambda x: ['', 'add', 'tests'][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Alias request created. Switch your nick to tests and call \".alias add Testsworth\" to confirm.")

    def test_alias7(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases.append(["happy", "joyous"])
        self.input.group = lambda x: ['', 'list', 'happy'][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("happy's current aliases are: happy, joyous.")

    def test_alias8(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases.append(["Testsworth", "tests"])
        self.input.group = lambda x: ['', 'list', None][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Your current aliases are: Testsworth, tests.")

    def test_alias9(self):
        self.input.nick = 'Testsworth'
        tell.nick_aliases.append(["Testsworth", "tests"])
        self.input.group = lambda x: ['', 'remove'][x]

        tell.alias(self.phenny, self.input)
        self.assertTrue(tell.aliasGroupFor('Testsworth') == ['Testsworth'])
        self.phenny.reply.assert_called_once_with("You have removed Testsworth from its alias group")

    def test_alias9(self):
        self.input.group = lambda x: ['', 'eat'][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Usage: .alias add <nick>, .alias list <nick>?, .alias remove")

    def test_alias10(self):
        self.input.group = lambda x: ['', None][x]

        tell.alias(self.phenny, self.input)
        self.phenny.reply.assert_called_once_with("Usage: .alias add <nick>, .alias list <nick>?, .alias remove")

