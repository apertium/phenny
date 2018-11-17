import unittest
from mock import MagicMock
from modules import issue

class TestIssue(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        
    def test_issue(self):
        test = ['.issue', 'octocat/Hello-World Create an illegal issue.']
        self.assertTrue(issue.issue(test) == 'invalid input')
        test = ['.issue', 'apertium/hypothetical-long-named-repository-apertium-hopefully-would-never-create Create an issue on a nonexistent repo.'][x]
        self.assertTrue(issue.issue(test) == 'not found')
        test = ['.issue', 'boing boing boing someone is hungry']
        self.assertTrue(issue.issue(test) == 'invalid input')
