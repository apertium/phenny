"""
test_ping.py - tests for the ping module
author: nu11us <work.willeggleston@gmail.com>
"""
import unittest
from mock import MagicMock
from modules import ping
import tools


class TestPing(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
        self.phenny.nick = "user"
        self.phenny.config.host = "host"

    def test_get_guests_user(self):
        self.input.admin = False
        ping.getGuests(self.phenny, self.input)
        out = self.phenny.reply.call_args[0][0]
        self.assertTrue("admin-only" in out)
    """
    def test_get_guests_admin(self):
        self.input.admin = True
        tools.db_path(self.phenny, 'guests')
        tools.write_db(self.phenny, 'guests', 'token')
        ping.getGuests(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("token" in out)
    """
    def test_interjection(self):
        self.input.nick = "user"
        ping.interjection(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertTrue("user!" in out)
