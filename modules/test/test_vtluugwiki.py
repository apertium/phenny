"""
test_vtluugwiki.py - tests for the VTLUUG wiki module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import re
import unittest
from mock import MagicMock
from modules import vtluugwiki
from web import catch_timeout


class TestVtluugwiki(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    @catch_timeout
    def test_vtluug(self):
        self.input.groups.return_value = ['', "VT-Wireless"]
        vtluugwiki.vtluug(self.phenny, self.input)
        out = self.phenny.say.call_args[0][0]
        m = re.search(r'https://vtluug[.]org/wiki/VT-Wireless',
                out, flags=re.UNICODE)
        self.assertTrue(m)

    @catch_timeout
    def test_vtluug_invalid(self):
        term = "EAP-TLS#netcfg"
        self.input.groups.return_value = ['', term]
        vtluugwiki.vtluug(self.phenny, self.input)
        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "the VTLUUG Wiki for \"{0}\".".format(term))

    @catch_timeout
    def test_vtluug_none(self):
        term = "Ajgoajh"
        self.input.groups.return_value = ['', term]
        vtluugwiki.vtluug(self.phenny, self.input)
        self.phenny.say.assert_called_once_with( "Can't find anything in "\
                "the VTLUUG Wiki for \"{0}\".".format(term))
