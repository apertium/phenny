import unittest, json
from mock import MagicMock, patch
from modules import issue

class TestIssue(unittest.TestCase):
    
    def setUp(self):
        self.phenny = MagicMock()
        self.phenny.nick = 'phenny'
        self.phenny.config.gh_oauth_token = 'test_token'
        
        self.input = MagicMock()
        self.input.nick = 'tester'
        
        issue.allowed_owners = ['test']
        
    @patch('modules.issue.post')
    def test_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.return_value = '{"html_url": "https://github.com/test/test"}'
        mock_post.return_value = mock_response.return_value
        
        mock_body = json.dumps({ "title": "Create a test issue.", "body": "This issue was automatically made by begiak, Apertium\'s beloved IRC bot, by the order of tester on #apertium. A human is yet to update the description."})
        mock_head = {'Authorization': 'token test_token'}
        self.input.group = lambda x: ['.issue', 'test/test Create a test issue.'][x]
        self.input.group.return_value = mock_response
        issue.issue(self.phenny, self.input)
        
        mock_post.assert_called_with('https://api.github.com/repos/test/test/issues', mock_body, mock_head)
        self.phenny.reply.assert_called_with('Issue created. You can add a description at https://github.com/test/test')
             
    def test_illegal(self):
        self.input.group = lambda x: ['.issue', 'octocat/Hello-World Create an illegal issue.'][x]
        self.input.group.return_value = 'Begiak cannot create an issue there.'
        issue.issue(self.phenny, self.input)
        self.phenny.reply.assert_called_with('Begiak cannot create an issue there.')
        
    def test_invalid(self):
        self.input.group = lambda x: ['.issue', 'boing boing boing someone is hungry'][x]
        self.input.group.return_value = 'Invalid .issue command. Usage: .issue <owner>/<repository> <title>'
        issue.issue(self.phenny, self.input)
        self.phenny.reply.assert_called_with('Invalid .issue command. Usage: .issue <owner>/<repository> <title>')
