import unittest
from mock import MagicMock
from modules import issue

class TestIssue(unittest.TestCase):
    
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        
    @patch('modules.issue.post')
    def test_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'html_url': 'https://github.com/test/test'
        }
        mock_post.return_value = mock_response
        self.input.group = lambda x: ['.issue' 'test/test Create a test issue.'][x]
        self.input.group.return_value = mock_response
        issue.issue(self.phenny, self.input)
        self.phenny.reply.assert_called_with('Issue created. You can add a description at https://github.com/test/test')
             
    def test_illegal(self):
        self.input.group = lambda x: = ['.issue', 'octocat/Hello-World Create an illegal issue.']
        self.input.group.return_value = 'Begiak cannot create an issue there.'
        issue.issue(self.phenny, self.input)
        self.phenny.reply.assert_called_with('Begiak cannot create an issue there.')
        
    def test_invalid(self):
        self.input.group = lambda x: = ['.issue', 'boing boing boing someone is hungry']
        self.input.group.return_value = 'Invalid .issue command. Usage: .issue <owner>/<repository> <title>'
        issue.issue(self.phenny, self.input)
        self.phenny.reply.assert_called_with('Invalid .issue command. Usage: .issue <owner>/<repository> <title>')
