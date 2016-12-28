# coding=utf-8
'''
test_apy.py: unit tests for the APy module (apy.py)
author: shardulc
'''

import unittest
import mock
import modules.apy as apy
from tools import GrumbleError
from json import dumps
from web import quote
from urllib.error import HTTPError


@mock.patch.object(apy.urllib.request.OpenerDirector, 'open')
class TestAPy(unittest.TestCase):

    def setUp(self):
        self.phenny = mock.MagicMock()
        self.input = mock.MagicMock()

        self.phenny.config.APy_url = 'http://faketestapy.com:2737'
        self.phenny.config.APy_analyseURL = 'http://faketestapy.com:2737'
        self.trans_query = '{:s}/translate?q={:s}&langpair={:s}|{:s}'
        self.texts = {
            'eng': 'english text',
            'spa': 'spanish text',
            'fra': 'french text',
            'cat': 'catalan text',
            'eng_long': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod \
                tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis \
                nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis \
                aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat \
                nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui \
                officia deserunt mollit anim id est laborum.'
        }

    def fake_json(self, lang):
        return bytes(dumps({'responseData': {'translatedText': self.texts[lang]}}), 'utf-8')

    def format_query(self, in_lang, out_lang):
        return self.trans_query.format(
            self.phenny.config.APy_url, quote(self.texts[in_lang]), in_lang, out_lang)

    def reset_mocks(self, *mocks):
        for moc in mocks:
            moc.reset_mock()

    def test_translate_langs(self, mock_open):
        # single language
        self.input.group.return_value = 'eng-spa ' + self.texts['eng']
        mock_open.return_value.read.return_value = self.fake_json('spa')
        apy.apertium_translate(self.phenny, self.input)
        mock_open.assert_called_once_with(self.format_query('eng', 'spa'))
        self.phenny.reply.assert_called_once_with(self.texts['spa'])
        self.reset_mocks(self.phenny, mock_open)

        # multiple languages
        langs = ['eng', 'fra', 'cat']
        self.input.group.return_value = '{:s} {:s}'.format(
            ' '.join(['spa-' + lg for lg in langs]), self.texts['spa'])
        mock_open.return_value.read.side_effect = [self.fake_json(lg) for lg in langs]
        apy.apertium_translate(self.phenny, self.input)
        assert mock_open.call_args_list == [mock.call(self.format_query('spa', lg)) for lg in langs]
        assert self.phenny.reply.call_args_list == [mock.call(self.texts[lg]) for lg in langs]
        self.reset_mocks(self.phenny, mock_open)

        # self-translation
        self.input.group.return_value = 'en-en Translate to the same language?'
        try:
            apy.apertium_translate(self.phenny, self.input)
            raise AssertionError('No exception raised for self-translation!')
        except GrumbleError:
            pass
        self.reset_mocks(self.phenny, mock_open)

    @mock.patch('modules.apy.handle_error')
    def test_translate_non_langs(self, mock_handle, mock_open):
        mock_handle.side_effect = GrumbleError('some message')

        # non-existent language
        self.input.group.return_value = 'spa-zzz ' + self.texts['spa']
        mock_open.side_effect = HTTPError('url', 400, 'msg', 'hdrs', 'fp')
        apy.apertium_translate(self.phenny, self.input)
        assert mock_handle.called
        self.phenny.say.assert_called_once_with('spa-zzz: some message')
        self.reset_mocks(self.phenny, mock_open, mock_handle)

        # bad input
        for inp in [self.texts['spa'], 'spa ' + self.texts['spa'], 'spa-eng']:
            self.input.group.return_value = inp
            try:
                apy.apertium_translate(self.phenny, self.input)
                raise AssertionError('No exception raised for missing translation parameters!')
            except GrumbleError:
                pass
        self.reset_mocks(self.phenny, mock_open, mock_handle)

        # non-existent language with actual language
        self.input.group.return_value = 'spa-eng spa-zzz ' + self.texts['spa']
        mock_open.side_effect = [mock.MagicMock(read=lambda: self.fake_json('eng')),
                                 HTTPError('url', 400, 'msg', 'hdrs', 'fp')]
        apy.apertium_translate(self.phenny, self.input)
        assert mock_open.call_args_list == [mock.call(self.format_query('spa', 'eng')),
                                            mock.call(self.format_query('spa', 'zzz'))]
        assert mock_handle.called
        self.phenny.reply.assert_called_once_with(self.texts['eng'])
        self.phenny.say.assert_called_once_with('spa-zzz: some message')
        self.reset_mocks(self.phenny, mock_open, mock_handle)

    def test_translate_admin(self, mock_open):
        self.input.group.return_value = 'eng-spa ' + self.texts['eng_long']

        # restricted length for non-admin
        self.input.admin = False
        try:
            apy.apertium_translate(self.phenny, self.input)
            raise AssertionError('No exception raised for long non-admin translation!')
        except GrumbleError:
            pass
        self.reset_mocks(self.phenny, mock_open)

        # non-restricted length for admin
        self.input.admin = True
        mock_open.return_value.read.return_value = self.fake_json('spa')
        apy.apertium_translate(self.phenny, self.input)
        mock_open.assert_called_once_with(self.trans_query.format(
            self.phenny.config.APy_url, quote(self.texts['eng_long']), 'eng', 'spa'))
        self.phenny.reply.assert_called_once_with(self.texts['spa'])
        self.reset_mocks(self.phenny, mock_open)

    def test_lists(self, mock_open):
        mock_open.return_value.read.return_value = bytes(dumps(
            {'responseData': [{'sourceLanguage': 'eng', 'targetLanguage': 'spa'},
                              {'sourceLanguage': 'spa', 'targetLanguage': 'eng'},
                              {'sourceLanguage': 'spa', 'targetLanguage': 'fra'}]}), 'utf-8')

        # single languages
        apy.apertium_listlangs(self.phenny, self.input)
        mock_open.assert_called_once_with(self.phenny.config.APy_url + '/listPairs')
        for lang in ['eng', 'spa', 'fra']:
            assert lang in self.phenny.say.call_args[0][0]
        self.reset_mocks(self.phenny, mock_open)

        # language pairs
        self.input.group.return_value = ''
        apy.apertium_listpairs(self.phenny, self.input)
        mock_open.assert_called_once_with(self.phenny.config.APy_url + '/listPairs')
        for pair in ['eng  →  spa', 'spa  →  eng', 'spa  →  fra']:
            assert pair in self.phenny.say.call_args[0][0]
        self.reset_mocks(self.phenny, mock_open)

        # language pairs for a given language
        self.input.group.return_value = 'spa'
        apy.apertium_listpairs(self.phenny, self.input)
        mock_open.assert_called_once_with(self.phenny.config.APy_url + '/listPairs')
        self.phenny.say.assert_called_once_with('eng  →  spa  →  eng, fra')
        self.reset_mocks(self.phenny, mock_open)

    @mock.patch('modules.apy.more.add_messages')
    def test_analyze_generate(self, mock_addmsgs, mock_open):
        # analyze
        anas = [['analyze/analyze<tags>', 'analyze'], ['this/this<tags>', 'this']]
        self.input.group.return_value = 'eng analyze this'
        mock_open.return_value.read.return_value = bytes(dumps(anas), 'utf-8')
        apy.apertium_analyse(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/analyse?lang={:s}&q={:s}'.format(
            self.phenny.config.APy_analyseURL, 'eng', quote('analyze this')))
        msgs = '\n'.join(['{:s}  →  {:s}'.format(orig, ana) for ana, orig in anas])
        assert mock_addmsgs.call_args[0] == (self.input.nick, self.phenny, msgs)
        self.reset_mocks(mock_open, mock_addmsgs)

        # generate
        gens = [['generate', '^generate<tags>$']]
        self.input.group.return_value = 'eng ^generate<tags>$'
        mock_open.return_value.read.return_value = bytes(dumps(gens), 'utf-8')
        apy.apertium_generate(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/generate?lang={:s}&q={:s}'.format(
            self.phenny.config.APy_analyseURL, 'eng', quote('^generate<tags>$')))
        msgs = '\n'.join(['{:s}  →  {:s}'.format(orig, gen) for gen, orig in gens])
        assert mock_addmsgs.call_args[0] == (self.input.nick, self.phenny, msgs)
        self.reset_mocks(mock_open, mock_addmsgs)

    @mock.patch('modules.apy.more.add_messages')
    def test_identlang(self, mock_addmsgs, mock_open):
        langs = {'eng': 1.0, 'fra': 0.2, 'spa': 0.0}
        self.input.group.return_value = self.texts['eng']
        mock_open.return_value.read.return_value = bytes(dumps(langs), 'utf-8')
        apy.apertium_identlang(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/identifyLang?q={:s}'.format(
            self.phenny.config.APy_url, quote(self.texts['eng'])))
        msgs = '\n'.join(['{:s} = {:s}'.format(lg, str(val)) for lg, val in langs.items()])
        assert mock_addmsgs.call_args[0] == (self.input.nick, self.phenny, msgs)
        self.reset_mocks(mock_open, mock_addmsgs)

    def test_stats(self, mock_open):
        # asserting only that the appropriate request is made; reporting is customizable
        try:
            apy.apertium_stats(self.phenny, self.input)
        except TypeError:
            pass
        mock_open.assert_called_once_with(self.phenny.config.APy_url + '/stats')
        self.reset_mocks(mock_open)

    def test_coverage(self, mock_open):
        self.input.group.return_value = 'eng ' + self.texts['eng']
        mock_open.return_value.read.return_value = bytes(dumps([0.9]), 'utf-8')
        apy.apertium_calccoverage(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/calcCoverage?lang={:s}&q={:s}'.format(
            self.phenny.config.APy_url, 'eng', quote(self.texts['eng'])))
        self.phenny.say.assert_called_once_with('Coverage is 90.0%')
        self.reset_mocks(self.phenny, mock_open)

    def test_perword(self, mock_open):
        # valid perword functions
        words = ['two', 'words']
        funcs = ['tagger', 'morph']
        per = [
            {'input': 'two', 'tagger': ['two<tags>'], 'morph': ['two<tags1>', 'two<tags2>']},
            {'input': 'words', 'tagger': ['words<tags>'], 'morph': ['words<tags1>', 'words<tags2>']}
        ]
        self.input.group.return_value = 'fra ({:s}) {:s}'.format(' '.join(funcs), ' '.join(words))
        mock_open.return_value.read.return_value = bytes(dumps(per), 'utf-8')
        apy.apertium_perword(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/perWord?lang={:s}&modes={:s}&q={:s}'.format(
            self.phenny.config.APy_url, 'fra', '+'.join(funcs), quote(' '.join(words))))
        calls = []
        for word in per:
            calls.append(mock.call(word['input'] + ':'))
            for func in funcs:
                calls.append(mock.call('  {:9s}: {:s}'.format(func, ' '.join(word[func]))))
        assert self.phenny.say.call_args_list == calls
        self.reset_mocks(self.phenny, mock_open)

        # invalid perword function 'nonfunc'
        self.input.group.return_value = 'fra (tagger nonfunc) word'
        try:
            apy.apertium_perword(self.phenny, self.input)
            raise AssertionError('No exception raised for invalid perword function!')
        except GrumbleError:
            pass
