"""
This is a series of unit tests for the iso639.py module,
with ISO 639-3 data from the ethnologue.py module

author: william1835
"""
import unittest
from modules.test.command_test import CommandTest
import os
import mock
from modules import iso639
from web import catch_timeout


class TestISO639(CommandTest, unittest.TestCase):
    modules = ['iso639']

    @classmethod
    @catch_timeout
    def setUpClass(cls):
        cls.iso1_codes = ['en','fr','de','ca','es']
        cls.iso3_codes = ['eng','fra','deu','cat','spa']

        cls.iso1_to_iso3 = {iso1: iso3 for iso1, iso3 in\
            zip(cls.iso1_codes, cls.iso3_codes)
        }
        # Both 2-letter and 3-letter ISO codes
        cls.iso_to_lang = {
            'en': 'English',
            'fr': 'French',
            'de': 'German',
            'ca': 'Catalan',
            'es': 'Spanish',
            'eng': 'English',
            'fra': 'French',
            'deu': 'German',
            'cat': 'Catalan',
            'spa': 'Spanish',
        }

        cls.langs = ['English','French','German','Catalan','Spanish']

    def setUp(self):
        super().setUp()
        self.phenny.iso_data = self.iso_to_lang
        self.phenny.iso_conversion_data = self.iso1_to_iso3

    def iso3_to_iso1(self, code):
        for iso1, iso3 in self.iso1_to_iso3.items():
            if code == iso3:
                return iso1
        return ''

    def test_iso_code_scrape(self):
        for k, v in self.iso_to_lang.items():
            self.assertEqual(self.phenny.iso_data[k], v)

    def test_iso_code_convert_scrape(self):
        for iso1, iso3 in self.iso1_to_iso3.items():
            self.assertEqual(self.phenny.iso_data[iso1], self.phenny.iso_data[iso3].split(',')[0])

    def test_conversion_iso1(self):
        for iso1 in self.iso1_codes:
            self.check_response('.iso639 '+iso1,
                                iso1 + ', ' + self.iso1_to_iso3[iso1]
                                + ' = ' + self.iso_to_lang[iso1])

    def test_conversion_iso3(self):
        for iso3 in self.iso3_codes:
            self.check_response('.iso639 '+iso3,
                                iso3 + ', ' + self.iso3_to_iso1(iso3)
                                + ' = ' + self.iso_to_lang[iso3])

    def test_lang_search(self):
        for lang in self.langs:
            out = self.message_response('.iso639 '+lang)
            for k, v in self.phenny.iso_data.items():
                if lang in v:
                    self.assertIn(k + ' = ' + v, out)
