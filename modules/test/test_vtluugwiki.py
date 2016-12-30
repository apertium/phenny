"""
test_vtluugwiki.py - tests for the VTLUUG wiki module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import re
import unittest
import requests
from mock import MagicMock, Mock
from modules import vtluugwiki

# these tests are probably skipped because the vtluug.org website appears to be
# permanently down
class TestVtluugwiki(unittest.TestCase):
    def setUp(self):
        try:
            requests.get('https://vtluug.org/wiki/').raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            self.skipTest('VTLUUG wiki is down, skipping test.')
        self.phenny = MagicMock()

    def test_vtluug(self):
        input = Mock(groups=lambda: ['', "VT-Wireless"])
        vtluugwiki.vtluug(self.phenny, input)
        out = self.phenny.say.call_args[0][0]
        m = re.match('^.* - https:\/\/vtluug\.org\/wiki\/VT-Wireless$',
                out, flags=re.UNICODE)
        self.assertTrue(m)

    def test_vtluug_invalid(self):
        term = "EAP-TLS#netcfg"
        input = Mock(groups=lambda: ['', term])
        vtluugwiki.vtluug(self.phenny, input)
        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "the VTLUUG Wiki for \"{0}\".".format(term))

    def test_vtluug_none(self):
        term = "Ajgoajh"
        input = Mock(groups=lambda: ['', term])
        vtluugwiki.vtluug(self.phenny, input)
        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "the VTLUUG Wiki for \"{0}\".".format(term))
