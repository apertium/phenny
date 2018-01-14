"""
test_archwiki.py - tests for the arch wiki module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import archwiki
from web import catch_timeout


class TestArchwiki(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    @catch_timeout
    def test_awik(self):
        self.input.groups.return_value = ['', "KVM"]
        archwiki.awik(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        self.assertIn('https://wiki.archlinux.org/index.php/KVM', out)

    @catch_timeout
    def test_awik_invalid(self):
        term = "KVM#Enabling_KSM"
        self.input.groups.return_value = ['', term]
        archwiki.awik(self.phenny, self.input)
        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "the ArchWiki for \"{0}\".".format(term))

    @catch_timeout
    def test_awik_none(self):
        term = "Ajgoajh"
        self.input.groups.return_value = ['', term]
        archwiki.awik(self.phenny, self.input)
        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "the ArchWiki for \"{0}\".".format(term))
