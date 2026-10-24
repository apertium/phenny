"""
test_weather.py - tests for the weather module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from modules.test.command_test import CommandTest
from web import catch_timeout


class TestWeather(CommandTest, unittest.TestCase):
    modules = ['weather']

    @catch_timeout
    def test_locations(self):
        def check_location(result, expected):
            self.assertAlmostEqual(result[0], expected[0], delta=0.14)
            self.assertAlmostEqual(result[1], expected[1], delta=0.14)

        locations = [
            ('92121', (32.9, -117.2)),
            ('94110', (37.8, -122.4)),
            ('94041', (37.4, -122.1)),
            ('27959', (36.0, -75.6)),
            ('48067', (42.5, -83.1)),
            ('23606', (37.1, -76.5)),
            ('23113', (37.5, -77.6)),
            ('27517', (42.6, -7.8)),
            ('15213', (40.4, -80.0)),
            ('90210', (34.1, -118.3)),
            ('33109', (25.8, -80.1)),

            ("Berlin", (52.5, 13.4)),
            ("Paris", (48.9, 2.4)),
            ("Vilnius", (54.7, 25.3)),

            ('Blacksburg, VA', (37.2, -80.4)),
            ('Granger, IN', (41.7, -86.1)),
        ]

        for query, expected in locations:
            result = self.get_module().location(query)
            check_location(result, expected)

    @catch_timeout
    def test_code_94110(self):
        icao = self.get_module().code(self.phenny, '94110')
        self.assertEqual(icao, 'KSFO')

    @catch_timeout
    def test_airport(self):
        out = self.message_response('.weather KIAD')
        self.assertTrue(out)

    @catch_timeout
    def test_place(self):
        out = self.message_response('.weather KIAD')
        self.assertTrue(out)

    @catch_timeout
    def test_notfound(self):
        self.check_response('.weather Hell, Mars',
                            "No NOAA data available for that location.")
