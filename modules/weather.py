#!/usr/bin/env python
"""
weather.py - Phenny Weather Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import metar
import json
import web
from tools import deprecated, GrumbleError

r_from = re.compile(r'(?i)([+-]\d+):00 from')


def location(q):
    try:
        r = int(q)
        uri = 'https://nominatim.openstreetmap.org/search/?postalcode={query}&format=json'\
            .format(query=web.quote(q))
    except ValueError:
        uri = 'https://nominatim.openstreetmap.org/search/?q={query}&format=json'\
            .format(query=web.quote(q))
    results = web.get(uri)
    data = json.loads(results)

    if len(data) < 1:
        return '?', None, None

    display_name = data[0]['display_name']
    lat = float(data[0]['lat'])
    lon = float(data[0]['lon'])
    return display_name, lat, lon


def local(icao, hour, minute):
    uri = ('http://www.flightstats.com/' + 
             'go/Airport/airportDetails.do?airportCode=%s')
    try: bytes = web.get(uri % icao)
    except AttributeError:
        raise GrumbleError('A WEBSITE HAS GONE DOWN WTF STUPID WEB')
    m = r_from.search(bytes)
    if m:
        offset = m.group(1)
        lhour = int(hour) + int(offset)
        lhour = lhour % 24
        return (str(lhour) + ':' + str(minute) + ', ' + str(hour) + 
                  str(minute) + 'Z')
        # return (str(lhour) + ':' + str(minute) + ' (' + str(hour) + 
        #            ':' + str(minute) + 'Z)')
    return str(hour) + ':' + str(minute) + 'Z'


def code(phenny, search):
    from icao import data

    if search.upper() in [loc[0] for loc in data]:
        return search.upper()
    else:
        display_name, latitude, longitude = location(search)
        if not latitude or not longitude:
            return False
        sumOfSquares = (99999999999999999999999999999, 'ICAO')
        for icao_code, lat, lon in data:
            latDiff = abs(latitude - lat)
            lonDiff = abs(longitude - lon)
            diff = (latDiff * latDiff) + (lonDiff * lonDiff)
            if diff < sumOfSquares[0]:
                sumOfSquares = (diff, icao_code)
        return sumOfSquares[1]


def f_weather(phenny, input):
    """.weather <ICAO> - Show the weather at airport with the code <ICAO>."""
    icao_code = input.group(2)
    if not icao_code:
        return phenny.say("Try .weather London, for example?")

    icao_code = code(phenny, icao_code)

    if not icao_code:
        phenny.say("No ICAO code found, sorry")
        return

    uri = 'http://tgftp.nws.noaa.gov/data/observations/metar/stations/%s.TXT'
    try:
        bytes = web.get(uri % icao_code)
    except AttributeError:
        raise GrumbleError('OH CRAP NOAA HAS GONE DOWN THE WEB IS BROKEN')
    except web.HTTPError:
        phenny.say("No NOAA data available for that location.")
        return

    if 'Not Found' in bytes:
        phenny.say(icao_code + ": no such ICAO code, or no NOAA data")
        return

    phenny.say(str(metar.parse(bytes)))
f_weather.rule = (['weather'], r'(.*)')

if __name__ == '__main__':
    print(__doc__.strip())
