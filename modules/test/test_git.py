"""
test_git.py - tests for the git module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from mock import MagicMock
from modules import git
from threading import Thread


class TestGit(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_setup_server(self):
        git.setup_server(self.phenny)
        thread_status = git.httpd
        git.teardown(self.phenny)
        self.assertTrue(thread_status)

    def test_auto_start(self):
        self.input.nick = "begiak2"
        self.phenny.nick = "begiak2"
        self.phenny.phenny.config.githook_autostart = True
        git.auto_start(self.phenny, self.input)
        thread_status = git.httpd or Thread(target=git.httpd.serve_forever).isAlive()
        git.teardown(self.phenny)
        self.assertTrue(thread_status)

    def test_auto_start_fail(self):
        self.input.nick = "not_begiak2"
        self.phenny.nick = "begiak2"
        git.auto_start(self.phenny, self.input)
        self.assertFalse(git.httpd)

    def test_gitserver_status_down(self):
        git.teardown(self.phenny)
        self.input.admin = False
        self.input.group = lambda x: [None, 'status'][x]
        git.gitserver(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Server is down" in out) 

    def test_gitserver_status_up(self):
        self.input.admin = False
        self.input.group = lambda x: [None, 'status'][x]
        git.httpd = True
        git.gitserver(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        git.httpd = None
        self.assertTrue("Server is up" in out)

    def test_gitserver_status_down_admin(self):
        git.teardown(self.phenny)
        self.input.admin = True
        self.input.group = lambda x: [None, 'status'][x]
        git.gitserver(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Server is down" in out) 

    def test_gitserver_status_up_admin(self):
        self.input.admin = True
        self.input.group = lambda x: [None, 'status'][x]
        git.httpd = True
        git.gitserver(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        git.httpd = None
        self.assertTrue("Server is up" in out)

    def test_gitserver_stop_on(self):
        self.input.admin = True
        self.input.group = lambda x: [None, 'stop'][x]
        git.gitserver(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertFalse(git.httpd)

    def test_gitserver_stop_off(self):
        self.input.admin = True
        self.input.group = lambda x: [None, 'stop'][x]
        git.teardown(self.phenny)
        git.gitserver(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Server is already down" in out and not git.httpd) 

    def test_gitserver_start_on(self):
        self.input.admin = True
        self.input.group = lambda x: [None, 'start'][x]
        git.setup_server(self.phenny)
        git.gitserver(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("Server is already up" in out and git.httpd)

    def test_gitserver_start_off(self):
        self.input.admin = True
        self.input.group = lambda x: [None, 'start'][x]
        git.teardown(self.phenny)
        git.gitserver(self.phenny, self.input)
        self.assertTrue(git.httpd)

    def test_to_commit(self):
        self.input.group = lambda x: [None, '93dd6c960b6e55d70db6f6704b1304e0e4101d49'][x]
        git.to_commit(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        real_url = "https://github.com/apertium/lttoolbox/commit/93dd6c960b6e55d70db6f6704b1304e0e4101d49"
        self.assertTrue(real_url in out)

    def test_retrieve_commit(self):
        self.phenny.config.git_repositories = ["lttoolbox"]
        self.input.group = lambda x: [None, "lttoolbox 93dd6c9"][x]
        git.retrieve_commit(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("Add a middle step to int before the final unsigned" in out)