"""
This is a series of unit tests for the iso639.py module,
with ISO 639-3 data from the ethnologue.py module

author: william1835
"""
import unittest
import os
import mock
from modules import iso639
from web import catch_timeout


class TestISO639(unittest.TestCase):

    @classmethod
    @catch_timeout
    def setUpClass(cls):
        cls.phenny = mock.MagicMock()
        cls.input = mock.MagicMock()

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
            'deu': 'German, Standard',
            'cat': 'Catalan',
            'spa': 'Spanish',
        }

        cls.langs = ['English','French','German','Catalan','Spanish']

        # Mock IRC data
        cls.phenny.config.host = 'irc.fakeserver.net'
        cls.phenny.nick = 'fakebot'

        iso639.setup(cls.phenny)

    def reset_mock(self, *mocks):
        for mock in mocks:
            mock.reset_mock()

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
            self.input.group.return_value = iso1
            iso639.iso639(self.phenny, self.input)
            self.phenny.say.assert_called_once_with(
                iso1 + ', ' + self.iso1_to_iso3[iso1]
                + ' = ' + self.iso_to_lang[iso1]
            )
            self.input.group.assert_called_once_with(2)
            self.reset_mock(self.phenny, self.input)

    def test_conversion_iso3(self):
        for iso3 in self.iso3_codes:
            self.input.group.return_value = iso3
            iso639.iso639(self.phenny, self.input)
            self.phenny.say.assert_called_once_with(
                iso3 + ', ' + self.iso3_to_iso1(iso3)
                + ' = ' + self.iso_to_lang[iso3]
            )
            self.input.group.assert_called_once_with(2)
            self.reset_mock(self.phenny, self.input)

    def test_lang_search(self):
        for lang in self.langs:
            self.input.group.return_value = lang
            iso639.iso639(self.phenny, self.input)
            phenny_say_return_value = self.phenny.say.call_args[0][0]
            for k, v in self.phenny.iso_data.items():
                if lang in v:
                    self.assertIn(k + ' = ' + v, phenny_say_return_value)
