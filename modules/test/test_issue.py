import unittest
import unittest.mock
import json
from modules.test.command_test import CommandTest

@unittest.mock.patch('web.is_up', return_value=True)
@unittest.mock.patch('web.post', return_value='{}')
class TestIssue(CommandTest, unittest.TestCase):
    modules = ['issue']

    def add_config(self):
        self.config.gh_oauth_token = 'test_token'
        self.config.git_issue_allowed_owners = ['test', 'apertium']

    def test_success(self, mock_post, mock_up):
        mock_post.return_value = '{"html_url": "https://github.com/test/test"}'
        mock_body = json.dumps({ "title": "Create a test issue.", "body": "This issue was automatically made by begiak, Apertium\'s beloved IRC bot, by the order of tester on #apertium. A human still needs to update the description."})
        mock_head = {'Authorization': 'token test_token'}
        self.check_response('.issue test/test Create a test issue.',
                            nick='tester',
                            expected='tester: Issue created. You should add a description at https://github.com/test/test')
        mock_post.assert_called_with('https://api.github.com/repos/test/test/issues', mock_body, mock_head)

    def test_illegal(self, mock_post, mock_up):
        self.check_response('.issue octocat/Hello-World Create an illegal issue.',
                            nick='tester',
                            expected='tester: Begiak cannot create an issue there.')

    def test_invalid(self, mock_post, mock_up):
        self.check_response('.issue boing/boing/boing boing boing someone is hungry',
                            nick='bob',
                            expected='bob: Invalid .issue command. Usage: .issue <owner>/<repository> <title>')
