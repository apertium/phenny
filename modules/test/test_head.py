"""
test_head.py - tests for the HTTP metadata utilities module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
import unittest.mock
from modules.test.command_test import CommandTest
from web import HTTPError

@unittest.mock.patch('modules.head.web.head')
class TestHead(CommandTest, unittest.TestCase):
    modules = ['head']

    def test_head(self, mock_head):
        mock_head.reset_mock()
        mock_head.return_value = {
            'Status': '200',
            'content-type': 'text/html; charset=utf-8',
            'last-modified': 'Thu, 29 Dec 2016 22:49:19 GMT',
            'content-length': '1000'
        }
        out = self.message_response('.head https://vtluug.org')
        mock_head.assert_called_once_with('https://vtluug.org')
        self.assertRegex(out,
                         r'200, text/html, utf-8, \d{4}\-\d{2}\-\d{2} ' +
                         r'\d{2}:\d{2}:\d{2} UTC, 1000 bytes, [0-9\.]+ s$')

    def test_head_404(self, mock_head):
        mock_head.reset_mock()
        mock_head.side_effect = HTTPError(response=unittest.mock.MagicMock(status_code='404'))
        out = self.message_response('.head https://vtluug.org/trigger_404')
        mock_head.assert_called_once_with('https://vtluug.org/trigger_404')
        self.assertIn('404', out)
        mock_head.reset_mock()

    def test_header(self, mock_head):
        mock_head.reset_mock()
        mock_head.return_value = {'server': 'HTTPlikeapro'}
        self.check_response('.head https://vtluug.org Server',
                            'Server: HTTPlikeapro')
        mock_head.assert_called_once_with('https://vtluug.org')
        mock_head.reset_mock()

    def test_header_bad(self, mock_head):
        mock_head.reset_mock()
        mock_head.return_value = {'server': 'HTTPlikeapro'}
        self.check_response('.head https://vtluug.org truncatedcone',
                            'There was no truncatedcone header in the response.')
        mock_head.assert_called_once_with('https://vtluug.org')
        mock_head.reset_mock()

    @unittest.mock.patch('modules.head.web.get')
    def test_snarfuri(self, mock_wget, mock_head):
        mock_head.reset_mock()
        mock_head.return_value = {
            'status': '200',
            'content-type': 'text/html; charset=utf-8'
        }
        mock_wget.return_value = '<html><title>Some Page</title></html>'
        self.assertFalse('https://www.somepage.com' in self.phenny.recent_titles)
        self.check_response('https://www.somepage.com',
                            '[ Some Page ]')
        self.assertTrue('https://www.somepage.com' in self.phenny.recent_titles)
        mock_head.assert_called_once_with('https://www.somepage.com')
        mock_wget.assert_called_once_with('https://www.somepage.com')

    @unittest.mock.patch('modules.head.requests.get')
    def test_snarfuri_405(self, mock_get, mock_head):
        mock_head.reset_mock()
        mock_head.side_effect = HTTPError(response=unittest.mock.MagicMock(status_code='405'))
        mock_get.side_effect = HTTPError(response=unittest.mock.MagicMock(status_code='405'))
        out = self.run_message('http://405notallowed.com')
        mock_head.assert_called_once_with('http://405notallowed.com')
        self.assertEqual(mock_get.call_args[0][0], 'http://405notallowed.com')
        self.assertEqual(out, [])
