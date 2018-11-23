import unittest
from mock import MagicMock
from modules import issue

class TestIssue(unittest.TestCase):
    
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        
    @patch('modules.issue.post')
    def testSuccess(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
        'html_url': 'https://github.com/test/test'
    }
    mock_post.return_value = mock_response
    self.input.group.return_value = 'test'
    issue.issue(self.phenny, self.input)
    self.phenny.reply.assert_called_with('Issue created. You can add a description at https://github.com/test/test')
             
    def testIllegal(self):
        test = ['.issue', 'octocat/Hello-World Create an illegal issue.']
        self.assertTrue(issue.issue(test) == 'Begiak cannot create an issue there.')
        
    def testInvalid(self):
        test = ['.issue', 'boing boing boing someone is hungry']
        self.assertTrue(issue.issue(test) == 'Invalid .issue command. Usage: .issue <owner>/<repository> <title>')
