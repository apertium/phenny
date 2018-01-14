"""
test_weather.py - tests for the weather module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import unittest
from mock import MagicMock
from modules import weather
from web import catch_timeouts


@catch_timeouts
class TestWeather(unittest.TestCase):

    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()

    def test_locations(self):
        def check_places(*args):
            def validate(actual_name, actual_lat, actual_lon):
                names = [n.strip() for n in actual_name.split(',')]
                for arg in args:
                    self.assertIn(arg, names)
            return validate

        locations = [
            # commented because the names keep changing, see goavki #305
#            ('92121', check_places("San Diego", "California")),
#            ('94110', check_places("SF", "California")),
#            ('94041', check_places("Mountain View", "California")),
#            ('27959', check_places("Dare County", "North Carolina")),
#            ('48067', check_places("Royal Oak", "Michigan")),
#            ('23606', check_places("Newport News", "Virginia")),
#            ('23113', check_places("Robious", "Virginia")),
#            ('27517', check_places("Chapel Hill", "North Carolina")),
#            ('15213', check_places("Allegheny County", "Pennsylvania")),
#            ('90210', check_places("LA", "California")),
#            ('33109', check_places("Fisher Island", "Florida")),
#            ('80201', check_places("Denver", "Colorado")),

            ("Berlin", check_places("Berlin", "Deutschland")),
            ("Paris", check_places("Paris", "Île-de-France")),
            ("Vilnius", check_places("Vilnius", "Lietuva")),

            ('Blacksburg, VA', check_places("Blacksburg", "Virginia")),
            ('Granger, IN', check_places("Granger", "Indiana")),
        ]

        for loc, validator in locations:
            names, lat, lon = weather.location(loc)
            validator(names, lat, lon)

    def test_code_94110(self):
        icao = weather.code(self.phenny, '94110')
        self.assertEqual(icao, 'KSFO')

    def test_airport(self):
        self.input.group.return_value = 'KIAD'
        weather.f_weather(self.phenny, self.input)
        self.assertTrue(self.phenny.say.called)

    def test_place(self):
        self.input.group.return_value = 'Blacksburg'
        weather.f_weather(self.phenny, self.input)
        self.assertTrue(self.phenny.say.called)

    def test_notfound(self):
        self.input.group.return_value = 'Hell'
        weather.f_weather(self.phenny, self.input)
        self.phenny.say.called_once_with('#phenny',
                "No NOAA data available for that location.")
