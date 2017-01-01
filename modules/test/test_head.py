"""
test_head.py - tests for the HTTP metadata utilities module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from web import HTTPError
from mock import MagicMock, patch
from modules import posted
from modules.head import head, snarfuri

@patch('modules.head.web.head')
class TestHead(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock(variables=['posted'], nick='phenny')
        self.phenny.config.host = 'irc.freenode.net'
        posted.DB_DIR = '.'
        posted.setup(self.phenny)
        self.input = MagicMock(sender='#phenny', nick='tester')

    def test_head(self, mock_head):
        self.input.group.return_value = 'https://vtluug.org'
        mock_head.return_value = {
            'Status': '200',
            'content-type': 'text/html; charset=utf-8',
            'last-modified': 'Thu, 29 Dec 2016 22:49:19 GMT',
            'content-length': '1000'
        }
        head(self.phenny, self.input)

        mock_head.assert_called_once_with('https://vtluug.org')
        out = self.phenny.reply.call_args[0][0]
        m = re.match('^200, text/html, utf-8, \d{4}\-\d{2}\-\d{2} '\
                '\d{2}:\d{2}:\d{2} UTC, 1000 bytes, [0-9\.]+ s$', out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_head_404(self, mock_head):
        self.input.group.return_value = 'https://vtluug.org/trigger_404'
        mock_head.side_effect = HTTPError(response=MagicMock(status_code='404'))
        head(self.phenny, self.input)
        mock_head.assert_called_once_with('https://vtluug.org/trigger_404')
        self.assertIn('404', self.phenny.say.call_args[0][0])

    def test_header(self, mock_head):
        self.input.group.return_value = 'https://vtluug.org Server'
        mock_head.return_value = {'server': 'HTTPlikeapro'}
        head(self.phenny, self.input)
        mock_head.assert_called_once_with('https://vtluug.org')
        self.phenny.say.assert_called_once_with('Server: HTTPlikeapro')

    def test_header_bad(self, mock_head):
        self.input.group.return_value = 'https://vtluug.org truncatedcone'
        mock_head.return_value = {'server': 'HTTPlikeapro'}
        head(self.phenny, self.input)
        mock_head.assert_called_once_with('https://vtluug.org')
        self.phenny.say.assert_called_once_with('There was no truncatedcone '
            'header in the response.')

    @patch('modules.head.web.get')
    @patch('modules.posted.requests.get')
    def test_snarfuri(self, mock_rget, mock_wget, mock_head):
        mock_head.return_value = {
            'status': '200',
            'content-type': 'text/html; charset=utf-8'
        }
        mock_wget.return_value = '<html><title>Some Page</title></html>'
        self.input.group.return_value = 'https://www.somepage.com'
        mock_rget.return_value.url = self.input.group.return_value
        snarfuri(self.phenny, self.input)
        mock_head.assert_called_once_with('https://www.somepage.com')
        mock_wget.assert_called_once_with('https://www.somepage.com')
        self.assertIn('Some Page', self.phenny.msg.call_args[0][1])

    @patch('modules.head.requests.get')
    def test_snarfuri_405(self, mock_get, mock_head):
        mock_head.side_effect = HTTPError(response=MagicMock(status_code='405'))
        mock_get.side_effect = HTTPError(response=MagicMock(status_code='405'))
        self.input.group.return_value = 'http://405notallowed.com'
        snarfuri(self.phenny, self.input)
        mock_head.assert_called_once_with('http://405notallowed.com')
        self.assertEqual(mock_get.call_args[0][0], 'http://405notallowed.com')
        self.assertFalse(self.phenny.msg.called)
