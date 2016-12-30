"""
test_archwiki.py - tests for the arch wiki module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import unittest
import requests
from mock import MagicMock, Mock
from modules import archwiki


class TestArchwiki(unittest.TestCase):
    def setUp(self):
        try:
            requests.get('https://wiki.archlinux.org').raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            self.skipTest('ArchLinux wiki is down, skipping test.')
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_awik(self):
        self.input.groups.return_value = ['', "KVM"]
        archwiki.awik(self.phenny, self.input)

        out = self.phenny.say.call_args[0][0]
        self.assertIn('https://wiki.archlinux.org/index.php/KVM', out)

    def test_awik_invalid(self):
        term = "KVM#Enabling_KSM"
        self.input.groups.return_value = ['', term]
        archwiki.awik(self.phenny, self.input)

        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "the ArchWiki for \"{0}\".".format(term))

    def test_awik_none(self):
        term = "Ajgoajh"
        self.input.groups.return_value = ['', term]
        archwiki.awik(self.phenny, self.input)

        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "the ArchWiki for \"{0}\".".format(term))
