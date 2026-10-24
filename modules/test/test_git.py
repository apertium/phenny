"""
test_git.py - tests for the git module
author: nu11us <work.willeggleston@gmail.com>
"""

import unittest
from modules.test.command_test import CommandTest

class TestGit(CommandTest, unittest.TestCase):
    modules = ['git', 'more']

    def add_config(self):
        self.config.nick = 'phenny'

    def setUp(self):
        super().setUp()
        self.phenny.say = lambda msg: self.phenny.msg('#blah', msg)
        self.phenny.reply = lambda msg: self.phenny.msg('#blah', msg)

    def tearDown(self):
        super().tearDown()
        self.get_module().teardown(self.phenny)
        self.phenny.write_queue = []

    def test_setup_server(self):
        self.get_module().setup_server(self.phenny)
        self.assertTrue(self.get_module().httpd)
        self.get_module().teardown(self.phenny)

    def test_auto_start(self):
        self.phenny.nick = "begiak"
        self.phenny.config.githook_autostart = True
        self.run_event(':begiak!a@b JOIN #apertium')
        thread_status = self.get_module().httpd
        self.get_module().teardown(self.phenny)
        self.assertTrue(thread_status)

    def test_auto_start_fail(self):
        self.phenny.nick = "begiak"
        self.phenny.config.githook_autostart = True
        self.run_event(':not_begiak!a@b JOIN #apertium')
        thread_status = self.get_module().httpd
        self.get_module().teardown(self.phenny)
        self.assertFalse(thread_status)

    def test_gitserver_status_down(self):
        out = self.message_response('.gitserver status', nick='user')
        self.assertIn("Server is down", out)

    def test_gitserver_status_up(self):
        self.get_module().setup_server(self.phenny)
        out = self.message_response('.gitserver status', nick='user')
        self.assertIn("Server is up", out)

    def test_gitserver_status_down_admin(self):
        out = self.message_response('.gitserver status', nick='admin')
        self.assertIn("Server is down", out)

    def test_gitserver_status_up_admin(self):
        self.get_module().setup_server(self.phenny)
        out = self.message_response('.gitserver status', nick='admin')
        self.assertIn("Server is up", out)

    def test_gitserver_stop_on(self):
        out = self.message_response('.gitserver stop', nick='admin')
        self.assertFalse(self.get_module().httpd)

    def test_gitserver_stop_off(self):
        out = self.message_response('.gitserver stop', nick='admin')
        self.assertIn("Server is already down", out)
        self.assertFalse(self.get_module().httpd)

    def test_gitserver_start_on(self):
        self.get_module().setup_server(self.phenny)
        self.check_response('.gitserver start', nick='admin',
                            expected='admin: Server is already up!')
        self.assertTrue(self.get_module().httpd)

    def test_gitserver_start_off(self):
        self.get_module().teardown(self.phenny)
        self.run_message('.gitserver start', nick='admin')
        self.assertTrue(self.get_module().httpd)

    def test_to_commit(self):
        out = self.message_response('.to_commit 93dd6c960b6e55d70db6f6704b1304e0e4101d49')
        real_url = "https://github.com/apertium/lttoolbox/commit/93dd6c960b6e55d70db6f6704b1304e0e4101d49"
        self.assertIn(real_url, out)
