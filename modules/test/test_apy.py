# coding=utf-8
'''
test_apy.py: unit tests for the APy module (apy.py)
author: shardulc
'''
import unittest
import mock
from modules import apy
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

    def check_exceptions(self, bad_list, name, reason=None):
        if not reason:
            reason = 'invalid input to {:s}'.format(name.__name__)
        for inp in bad_list:
            self.input.group.return_value = inp
            with self.assertRaises(GrumbleError,
                                   msg='No exception raised for {:s}!'.format(reason)):
                name.__call__(self.phenny, self.input)

    def check_error(self, bad_list, name, error, reason=None):
        if not reason:
            reason = 'invalid input to {:s}'.format(name.__name__)
        if not isinstance(error, apy.Status):
            raise ValueError('Parameter error must be a Status.')
        for inp in bad_list:
            self.input.group.return_value = inp
            function_return_val = name.__call__(self.phenny, self.input)
            self.assertEqual(function_return_val, error, msg='No {:s} returned for {:s}!'.format(error.name, reason))

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
        self.assertEqual(mock_open.call_args_list,
                         [mock.call(self.format_query('spa', lg)) for lg in langs])
        self.assertEqual(self.phenny.reply.call_args_list,
                         [mock.call(self.texts[lg]) for lg in langs])
        self.reset_mocks(self.phenny, mock_open)

    @mock.patch('modules.apy.handle_error')
    def test_translate_non_langs(self, mock_handle, mock_open):
        mock_handle.side_effect = GrumbleError('some message')

        # non-existent language
        self.input.group.return_value = 'spa-zzz ' + self.texts['spa']
        mock_open.side_effect = HTTPError('url', 400, 'msg', 'hdrs', None)
        apy.apertium_translate(self.phenny, self.input)
        self.assertTrue(mock_handle.called)
        self.phenny.say.assert_called_once_with('spa-zzz: some message')
        self.reset_mocks(self.phenny, mock_open, mock_handle)

        # bad input
        self.check_error([self.texts['spa'], 'spa ' + self.texts['spa'], 'spa-eng'],
                              apy.apertium_translate, apy.Status.SYNTAX_ERROR)
        self.check_error(['en-en Translate to the same language?'],
                              apy.apertium_translate, apy.Status.ENUM_ERROR, 'self-translation')
        self.reset_mocks(self.phenny, mock_open, mock_handle)

        # non-existent language with actual language
        self.input.group.return_value = 'spa-eng spa-zzz ' + self.texts['spa']
        mock_open.side_effect = [mock.MagicMock(read=lambda: self.fake_json('eng')),
                                 HTTPError('url', 400, 'msg', 'hdrs', None)]
        apy.apertium_translate(self.phenny, self.input)
        self.assertEqual(mock_open.call_args_list, [mock.call(self.format_query('spa', 'eng')),
                                                    mock.call(self.format_query('spa', 'zzz'))])
        self.assertTrue(mock_handle.called)
        self.phenny.reply.assert_called_once_with(self.texts['eng'])
        self.phenny.say.assert_called_once_with('spa-zzz: some message')

    def test_translate_admin(self, mock_open):
        self.input.group.return_value = 'eng-spa ' + self.texts['eng_long']

        # restricted length for non-admin
        self.input.admin = False
        self.check_error(['eng-spa ' + self.texts['eng_long']],
                              apy.apertium_translate, apy.Status.SYNTAX_ERROR,
                              'long non-admin translation!')
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
        langs = ['eng', 'spa', 'fra']
        pairs = [('eng', 'spa'), ('spa', 'eng'), ('spa', 'fra')]
        mock_open.return_value.read.return_value = bytes(dumps(
            {'responseData': [{'sourceLanguage': inlg, 'targetLanguage': outlg}
                              for inlg, outlg in pairs]}), 'utf-8')

        # single languages
        apy.apertium_listlangs(self.phenny, self.input)
        mock_open.assert_called_once_with(self.phenny.config.APy_url + '/listPairs')
        for lang in langs:
            self.assertIn(lang, self.phenny.say.call_args[0][0])
        self.reset_mocks(self.phenny, mock_open)

        # language pairs
        self.input.group.return_value = ''
        apy.apertium_listpairs(self.phenny, self.input)
        mock_open.assert_called_once_with(self.phenny.config.APy_url + '/listPairs')
        for pair in pairs:
            self.assertIn('{:s}  →  {:s}'.format(*pair), self.phenny.say.call_args[0][0])
        self.reset_mocks(self.phenny, mock_open)

        # language pairs for a given language
        lang = 'spa'
        self.input.group.return_value = lang
        to_lang = []
        from_lang = []
        for pair in pairs:
            if pair[0] == lang:
                to_lang.append(pair[1])
            if pair[1] == lang:
                from_lang.append(pair[0])
        apy.apertium_listpairs(self.phenny, self.input)
        mock_open.assert_called_once_with(self.phenny.config.APy_url + '/listPairs')
        apy_from_lang, lang, apy_to_lang = self.phenny.say.call_args[0][0].split('  →  ')
        self.assertEqual(set(to_lang), set(apy_to_lang.split(', ')))
        self.assertEqual(set(from_lang), set(apy_from_lang.split(', ')))
        self.reset_mocks(self.phenny, mock_open)

    @mock.patch('modules.apy.more.add_messages')
    def test_analyze_generate(self, mock_addmsgs, mock_open):
        # analyze
        words = ['analyze', 'this']
        anas = [['{0}/{0}<tags>'.format(word), word] for word in words]
        self.input.group.return_value = 'eng ' + ' '.join(words)
        mock_open.return_value.read.return_value = bytes(dumps(anas), 'utf-8')
        apy.apertium_analyse(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/analyse?lang={:s}&q={:s}'.format(
            self.phenny.config.APy_analyseURL, 'eng', quote(' '.join(words))))
        msgs = ['{:s}  →  {:s}'.format(orig, ana) for ana, orig in anas]
        self.assertEqual(mock_addmsgs.call_args[0][2], msgs)
        self.reset_mocks(mock_open, mock_addmsgs)

        # generate
        gens = [['generate', '^generate<tags>$']]
        self.input.group.return_value = 'eng ^generate<tags>$'
        mock_open.return_value.read.return_value = bytes(dumps(gens), 'utf-8')
        apy.apertium_generate(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/generate?lang={:s}&q={:s}'.format(
            self.phenny.config.APy_analyseURL, 'eng', quote('^generate<tags>$')))
        msgs = ['{:s}  →  {:s}'.format(orig, gen) for gen, orig in gens]
        self.assertEqual(mock_addmsgs.call_args[0][2], msgs)
        self.reset_mocks(mock_open, mock_addmsgs)

        # bad input
        self.check_error([' '.join(words), 'eng'], apy.apertium_analyse, apy.Status.SYNTAX_ERROR)
        self.check_error([' '.join(words), 'eng'], apy.apertium_generate, apy.Status.SYNTAX_ERROR)

    @mock.patch('modules.apy.more.add_messages')
    def test_identlang(self, mock_addmsgs, mock_open):
        langs = {'eng': 1.0, 'fra': 0.2, 'spa': 0.0}
        self.input.group.return_value = self.texts['eng']
        mock_open.return_value.read.return_value = bytes(dumps(langs), 'utf-8')
        apy.apertium_identlang(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/identifyLang?q={:s}'.format(
            self.phenny.config.APy_url, quote(self.texts['eng'])))
        msgs = set('{:s} = {:s}'.format(lg, str(val)) for lg, val in langs.items())
        self.assertEqual(set(mock_addmsgs.call_args[0][2]), msgs)
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
        # good input
        self.input.group.return_value = 'eng ' + self.texts['eng']
        mock_open.return_value.read.return_value = bytes(dumps([0.9]), 'utf-8')
        apy.apertium_calccoverage(self.phenny, self.input)
        mock_open.assert_called_once_with('{:s}/calcCoverage?lang={:s}&q={:s}'.format(
            self.phenny.config.APy_url, 'eng', quote(self.texts['eng'])))
        self.phenny.say.assert_called_once_with('Coverage is 90.0%')
        self.reset_mocks(self.phenny, mock_open)

        # bad input
        self.check_error(['eng', self.texts['eng'], 'eng-spa'], apy.apertium_calccoverage, apy.Status.SYNTAX_ERROR)

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
        self.assertEqual(self.phenny.say.call_args_list, calls)
        self.reset_mocks(self.phenny, mock_open)

        # bad input
        self.check_exceptions(['fra (tagger nonfunc) word'], apy.apertium_perword,
                              'invalid perword function')
        self.check_error(['fra', 'fra (tagger)', '(tagger)', 'fra word',
                               '(tagger morph) word'], apy.apertium_perword,
                               apy.Status.SYNTAX_ERROR)
