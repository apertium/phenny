# coding=utf-8
'''
test_apy.py: unit tests for the APy module (apy.py)
author: shardulc
'''
import unittest
import unittest.mock
from modules.test.command_test import CommandTest
from tools import GrumbleError
from json import dumps
from web import quote
import collections

@unittest.mock.patch('web.api_call')
class TestAPy(CommandTest, unittest.TestCase):
    modules = ['apy', 'more']

    def add_config(self):
        self.config.APy_url = 'http://faketestapy.com:2737'
        self.config.APy_analyseURL = 'http://faketestapy.com:2737'
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
        return {'responseData': {'translatedText': self.texts[lang]}}

    def format_query(self, in_lang, out_lang):
        return self.trans_query.format(
            self.phenny.config.APy_url, quote(self.texts[in_lang]), in_lang, out_lang)

    def check_api(self, mock_open, uri):
        h = self.get_module().headers
        if isinstance(uri, list):
            self.assertEqual(mock_open.call_args_list,
                             [unittest.mock.call(u, headers=h) for u in uri])
        else:
            mock_open.assert_called_once_with(uri, headers=h)
        mock_open.reset_mock()

    def test_translate_langs(self, mock_open):
        # single language
        mock_open.return_value = self.fake_json('spa')
        self.check_response('.t eng-spa '+self.texts['eng'],
                            nick='person',
                            expected='person: '+self.texts['spa'])
        self.check_api(mock_open, self.format_query('eng', 'spa'))

        # multiple languages
        langs = ['eng', 'fra', 'cat']
        mock_open.side_effect = [self.fake_json(lg) for lg in langs]

        inp = '{:s} {:s}'.format(
            ' '.join(['spa-' + lg for lg in langs]), self.texts['spa'])
        out = self.run_message('.t '+inp, nick='person', channel='#ch')
        self.check_api(mock_open,
                       [self.format_query('spa', lg) for lg in langs])
        self.assertEqual(out, ['PRIVMSG #ch :person: '+self.texts[lg]
                               for lg in langs])

    def test_translate_non_langs(self, mock_open):
        # non-existent language
        mock_open.side_effect = GrumbleError('no such language')
        out = self.check_response('.t spa-zzz '+self.texts['spa'],
                                  'spa-zzz: no such language')
        self.assertTrue(mock_open.called)
        mock_open.reset_mock()

        # bad input
        for bad in [self.texts['spa'], 'spa ' + self.texts['spa'], 'spa-eng']:
            self.check_response('.t '+bad,
                                'Usage: .t en-es|es-fr en-ca I like pie')
        self.check_response('.t en-en Translate to the same language?',
                            'Stop trying to confuse me! Pick different languages ;)')
        mock_open.reset_mock()

        # non-existent language with actual language
        mock_open.side_effect = [self.fake_json('eng'),
                                 GrumbleError('no such language zzz')]
        out = self.run_message('.t spa-eng spa-zzz '+self.texts['spa'],
                               channel='#ch', nick='n')
        self.check_api(mock_open, [self.format_query('spa', 'eng'),
                                   self.format_query('spa', 'zzz')])
        self.assertEqual(out, ['PRIVMSG #ch :n: '+self.texts['eng'],
                               'PRIVMSG #ch :spa-zzz: no such language zzz'])

    def test_translate_admin(self, mock_open):
        # restricted length for non-admin
        self.check_response('.t eng-spa '+self.texts['eng_long'],
                            nick='non-admin',
                            expected='Phrase must be under 350 characters.')
        mock_open.reset_mock()

        # non-restricted length for admin
        mock_open.return_value = self.fake_json('spa')
        self.check_response('.t eng-spa '+self.texts['eng_long'],
                            nick='admin',
                            expected='admin: '+self.texts['spa'])
        self.check_api(mock_open, self.trans_query.format(
            self.phenny.config.APy_url, quote(self.texts['eng_long']), 'eng', 'spa'))

    def test_lists(self, mock_open):
        langs = ['eng', 'spa', 'fra']
        pairs = [('eng', 'spa'), ('spa', 'eng'), ('spa', 'fra')]
        mock_open.return_value = {'responseData': [
            {'sourceLanguage': inlg, 'targetLanguage': outlg}
            for inlg, outlg in pairs]}

        # single languages
        out = self.message_response('.listlangs')
        self.check_api(mock_open, self.phenny.config.APy_url + '/listPairs')
        for lang in langs:
            self.assertIn(lang, out)
        mock_open.reset_mock()

        # language pairs
        out = self.message_response('.listpairs')
        self.check_api(mock_open, self.phenny.config.APy_url + '/listPairs')
        for pair in pairs:
            self.assertIn('{:s}  →  {:s}'.format(*pair), out)

        # language pairs for a given language
        out = self.message_response('.listpairs spa')
        lang = 'spa'
        to_lang = []
        from_lang = []
        for pair in pairs:
            if pair[0] == lang:
                to_lang.append(pair[1])
            if pair[1] == lang:
                from_lang.append(pair[0])
        self.check_api(mock_open, self.phenny.config.APy_url + '/listPairs')
        apy_from_lang, lang, apy_to_lang = out.split('  →  ')
        self.assertEqual(set(to_lang), set(apy_to_lang.split(', ')))
        self.assertEqual(set(from_lang), set(apy_from_lang.split(', ')))

    def test_analyze_generate(self, mock_open):
        # analyze
        words = ['analyze', 'this']
        anas = [['{0}/{0}<tags>'.format(word), word] for word in words]
        mock_open.return_value = anas
        out = self.run_message('.analyze eng ' + ' '.join(words),
                               channel='#ch', nick='n')
        self.check_api(mock_open, '{:s}/analyse?lang={:s}&q={:s}'.format(
            self.phenny.config.APy_analyseURL, 'eng', quote(' '.join(words))))
        msgs = ['PRIVMSG n :n: {:s}  →  {:s}'.format(orig, ana)
                for ana, orig in anas]
        self.assertEqual(out, msgs)
        mock_open.reset_mock()

        # generate
        gens = [['generate', '^generate<tags>$']]
        mock_open.return_value = gens
        out = self.run_message('.generate eng ^generate<tags>$',
                               nick='bob')
        self.check_api(mock_open, '{:s}/generate?lang={:s}&q={:s}'.format(
            self.phenny.config.APy_analyseURL, 'eng', quote('^generate<tags>$')))
        msgs = ['PRIVMSG bob :bob: {:s}  →  {:s}'.format(orig, gen)
                for gen, orig in gens]
        self.assertEqual(out, msgs)

        # bad input
        self.check_response('.analyze '+' '.join(words),
                            'Usage: .analyse kaz Сен бардың ба')
        self.check_response('.analyze eng',
                            'Usage: .analyse kaz Сен бардың ба')
        self.check_response('.generate '+' '.join(words),
                            'Usage: .generate kaz ^сен<v><tv><imp><p2><sg>$')
        self.check_response('.generate eng',
                            'Usage: .generate kaz ^сен<v><tv><imp><p2><sg>$')

    def test_identlang(self, mock_open):
        langs = {'eng': 1.0, 'fra': 0.2, 'spa': 0.0}
        mock_open.return_value = langs
        self.get_module('apy').more.buffer_threshold = 5
        out = self.run_message('.identlang '+self.texts['eng'],
                               nick='bob')
        self.check_api(mock_open, '{:s}/identifyLang?q={:s}'.format(
            self.phenny.config.APy_url, quote(self.texts['eng'])))
        msgs = set('PRIVMSG bob :bob: {:s} = {:s}'.format(lg, str(val))
                   for lg, val in langs.items())
        self.assertEqual(set(out), msgs)

    def test_stats(self, mock_open):
        # asserting only that the appropriate request is made; reporting is customizable
        dct = collections.defaultdict(lambda: 2)
        dct['periodStats'] = collections.defaultdict(lambda: 2)
        dct['runningPipes'] = []
        mock_open.return_value = {'responseData': dct}
        self.run_message('.apystats')
        mock_open.assert_called_once_with(self.phenny.config.APy_url + '/stats', headers=self.get_module().headers)
        mock_open.reset_mock()

    def test_coverage(self, mock_open):
        # good input
        mock_open.return_value = [0.9]
        self.check_response(
            '.coverage eng '+self.texts['eng'],
            'Coverage is 90.0%')
        mock_open.assert_called_once_with(
            '{:s}/calcCoverage?lang={:s}&q={:s}'.format(
                self.phenny.config.APy_url, 'eng', quote(self.texts['eng'])),
            headers=self.get_module().headers)
        mock_open.reset_mock()

        # bad input
        for inp in ['eng', self.texts['eng'], 'eng-spa']:
            self.check_response(
                '.coverage '+inp,
                'Usage: .calccoverage en Whereas disregard and contempt for which have outraged the conscience of mankind')

    def test_perword(self, mock_open):
        # valid perword functions
        words = ['two', 'words']
        funcs = ['tagger', 'morph']
        per = [
            {'input': 'two', 'tagger': ['two<tags>'], 'morph': ['two<tags1>', 'two<tags2>']},
            {'input': 'words', 'tagger': ['words<tags>'], 'morph': ['words<tags1>', 'words<tags2>']}
        ]

        mock_open.return_value = per
        out = self.run_message('.perword fra ({:s}) {:s}'.format(' '.join(funcs), ' '.join(words)), channel='#apertium')
        mock_open.assert_called_once_with(
            '{:s}/perWord?lang={:s}&modes={:s}&q={:s}'.format(
                self.phenny.config.APy_url, 'fra', '+'.join(funcs), quote(' '.join(words))),
            headers=self.get_module().headers)
        calls = []
        for word in per:
            calls.append('PRIVMSG #apertium :' + word['input'] + ':')
            for func in funcs:
                calls.append('PRIVMSG #apertium :  {:9s}: {:s}'.format(func, ' '.join(word[func])))
        self.assertEqual(out, calls)
        mock_open.reset_mock()

        # bad input
        self.check_response(
            '.perword fra (tagger nonfunc) word',
            'The requested functions must be from the set biltrans, disambig, morph, tagger, translate.')
        bad = ['fra', 'fra (tagger)', '(tagger)', 'fra word',
               '(tagger morph) word']
        for inp in bad:
            self.check_response(
                '.perword '+inp,
                'Usage: .perword fr (tagger morph) Bonjour tout le monde!')
