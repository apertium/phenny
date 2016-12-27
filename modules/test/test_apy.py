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
        self.input.group.return_value = '{:s} {:s}'.format(' '.join(['spa-' + lang for lang in langs]), self.texts['spa'])
        mock_open.return_value.read.side_effect = [self.fake_json(lang) for lang in langs]
        apy.apertium_translate(self.phenny, self.input)
        for lang in langs:
            mock_open.assert_any_call(self.format_query('spa', lang))
            self.phenny.reply.assert_any_call(self.texts[lang])
        self.reset_mocks(self.phenny, mock_open)

        # self-translation
        self.input.group.return_value = 'en-en Translate to the same language?'
        try:
            apy.apertium_translate(self.phenny, self.input)
            raise AssertionError('No exception thrown for self-translation!')
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

        # non-existent language with actual language
        self.input.group.return_value = 'spa-eng spa-zzz ' + self.texts['spa']
        mock_open.side_effect = [mock.MagicMock(read=lambda: self.fake_json('eng')), HTTPError('url', 400, 'msg', 'hdrs', 'fp')]
        apy.apertium_translate(self.phenny, self.input)
        mock_open.assert_any_call(self.format_query('spa', 'eng'))
        mock_open.assert_any_call(self.format_query('spa', 'zzz'))
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
