# metar.py
# Copyright (c) 2013, mutantmonkey <mutantmonkey@mutantmonkey.in>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import datetime

INTENSITY = {
    "-": "light",
    "+": "heavy",
    "VC": "in the vicinity:",
}

DESCRIPTOR = {
    "MI": "shallow",
    "PR": "partial",
    "BC": "patches",
    "DR": "low drifting",
    "BL": "blowing",
    "SH": "showers",
    "TS": "thunderstorm",
    "FZ": "freezing",
}

PRECIPITATION = {
    "DZ": "drizzle",
    "RA": "rain",
    "SN": "snow",
    "SG": "snow grains",
    "IC": "ice crystals",
    "PL": "ice pellets",
    "GR": "hail",
    "GS": "small hail",
    "UP": "unknown precipitation",
}

OBSCURATION = {
    "BR": "mist",
    "FG": "fog",
    "VA": "volcanic ash",
    "DU": "widespread dust",
    "SA": "sand",
    "HZ": "haze",
    "PY": "spray",
}

CLOUD_COVER = {
    "SKC": "clear",
    "CLR": "clear",
    "NSC": "clear",
    "FEW": "a few clouds",
    "SCT": "scattered clouds",
    "BKN": "broken clouds",
    "OVC": "overcast",
    "VV": "indefinite ceiling",
}

OTHER = {
    "PO": "whirls",
    "SQ": "squals",
    "FC": "tornado",
    "SS": "sandstorm",
    "DS": "duststorm",
}

import re


class Weather(object):
    cover = None
    height = None
    wind_speed = None
    wind_direction = None
    intensity = None
    descriptor = None
    precipitation = None
    obscuration = None
    other = None
    conditions = None

    def describe_wind(self):
        if self.wind_speed is not None:
            if self.wind_speed < 0:
                return "unknown"
            elif self.wind_speed < 1:
                return "calm"
            elif self.wind_speed < 4:
                return "light air"
            elif self.wind_speed < 7:
                return "light breeze"
            elif self.wind_speed < 11:
                return "gentle breeze"
            elif self.wind_speed < 16:
                return "moderate breeze"
            elif self.wind_speed < 22:
                return "fresh breeze"
            elif self.wind_speed < 28:
                return "strong breeze"
            elif self.wind_speed < 34:
                return "near gale"
            elif self.wind_speed < 41:
                return "gale"
            elif self.wind_speed < 56:
                return "storm"
            elif self.wind_speed < 64:
                return "violent storm"
            else:
                return "hurricane"
        else:
            return 'unknown'

    def windsock(self):
        if self.wind_direction is not None:
            if (self.wind_speed <= 22.5) or (self.wind_speed > 337.5):
                return '\u2191'
            elif (self.wind_speed > 22.5) and (self.wind_speed <= 67.5):
                return '\u2197'
            elif (self.wind_speed > 67.5) and (self.wind_speed <= 112.5):
                return '\u2192'
            elif (self.wind_speed > 112.5) and (self.wind_speed <= 157.5):
                return '\u2198'
            elif (self.wind_speed > 157.5) and (self.wind_speed <= 202.5):
                return '\u2193'
            elif (self.wind_speed > 202.5) and (self.wind_speed <= 247.5):
                return '\u2199'
            elif (self.wind_speed > 247.5) and (self.wind_speed <= 292.5):
                return '\u2190'
            elif (self.wind_speed > 292.5) and (self.wind_speed <= 337.5):
                return '\u2196'
        else:
            return '?'

    def __repr__(self):
        chunks = []
        if self.cover:
            chunks.append(self.cover)

        chunks.append('{0}°C'.format(self.temperature))

        if self.pressure:
            chunks.append('{0} hPa'.format(self.pressure))

        if self.conditions:
            chunks.append(self.conditions)

        wind = self.wind_speed if self.wind_speed is not None else '?'
        chunks.append('{note} {speed} m/s ({windsock})'.format(
            note=self.describe_wind(),
            speed=wind,
            windsock=self.windsock()))

        ret = ', '.join(chunks) + ' - {station} {time}'
        return ret.format(station=self.station,
                          time=self.time.strftime("%H:%MZ"))


def build_regex(key, classifier):
    ret = "|".join([re.escape(x) for x in classifier.keys()])
    return r"(?P<{key}>{regex})".format(key=re.escape(key), regex=ret)


def weather_regex():
    ret = r'\s'
    ret += build_regex('intensity', INTENSITY) + r'?'
    ret += build_regex('descriptor', DESCRIPTOR) + r'?'
    ret += build_regex('precipitation', PRECIPITATION) + r'?'
    ret += build_regex('obscuration', OBSCURATION) + r'?'
    ret += build_regex('other', OTHER) + r'?'
    ret += r'\s'
    return re.compile(ret)


def parse_temp(t):
    if t[0] == 'M':
        return -int(t[1:])
    return int(t)


def parse(data):
    w = Weather()

    data = data.splitlines()
    metar = data[1].split()

    w.metar = data[1]
    w.station = metar[0]
    metar = metar[1:]

    # time
    time_re = re.compile(r"\d{2}(?P<hour>\d{2})(?P<min>\d{2})Z")
    m = time_re.search(w.metar)
    if m:
        w.time = datetime.time(hour=int(m.group('hour')),
                minute=int(m.group('min')))

    # mode
    #if metar[0] == "AUTO":
    #    metar = metar[1:]

    # wind speed
    wind_re = re.compile(r"(?P<direction>\d{3})(?P<speed>\d+)(G(?P<gust>\d+))?(?P<unit>KT|MPS)")
    m = wind_re.search(w.metar)
    if m:
        w.wind_direction = int(m.group('direction'))

        if m.group('unit') == "KT":
            # convert knots to m/s
            w.wind_speed = round(int(m.group('speed')) * 1852 / 3600)
            if m.group('gust'):
                w.wind_gust = round(int(m.group('speed')) * 1852 / 3600)
            else:
                w.wind_gust = None
        else:
            w.wind_speed = int(m.group('speed'))
            if m.group('gust'):
                w.wind_gust = int(m.group('gust'))
            else:
                w.wind_gust = None
        metar = metar[1:]

    # visibility
    # 0800N?
    visibility_re = re.compile(r"(?P<vis>(?P<dist>\d+)SM|(?P<disti>\d{4})\s|CAVOK)")
    m = visibility_re.search(w.metar)
    if m:
        if m.group('dist'):
            w.visibility = m.group('dist')
        elif m.group('disti'):
            w.visibility = m.group('disti')
        elif m.group('vis') == 'CAVOK':
            w.cover = "clear"
            w.visibility = m.group('vis')
    else:
        w.visibility = None

    # runway visibility range

    # conditions
    matches = weather_regex().finditer(w.metar)
    for m in matches:
        if not m:
            continue

        weather = []
        if m.group('intensity'):
            w.intensity = INTENSITY[m.group('intensity')]
            weather.append(w.intensity)
        if m.group('descriptor'):
            w.descriptor = DESCRIPTOR[m.group('descriptor')]
            weather.append(w.descriptor)
        if m.group('precipitation'):
            w.precipitation = PRECIPITATION[m.group('precipitation')]
            weather.append(w.precipitation)
        if m.group('obscuration'):
            w.obscuration = OBSCURATION[m.group('obscuration')]
            weather.append(w.obscuration)
        if m.group('other'):
            w.other = OTHER[m.group('other')]
            weather.append(w.other)
        if len(weather) > 0:
            w.conditions = " ".join(weather)

    # cloud cover
    cover_re = re.compile(build_regex('cover', CLOUD_COVER) +\
            r"(?P<height>\d*)")
    matches = cover_re.finditer(w.metar)
    for m in matches:
        w.cover = CLOUD_COVER[m.group('cover')]
        w.height = m.group('height')

    # temperature
    temp_re = re.compile(r"(?P<temp>[M\d]+)\/(?P<dewpoint>[M\d]+)")
    m = temp_re.search(w.metar)
    if m:
        w.temperature = parse_temp(m.group('temp'))
        w.dewpoint = parse_temp(m.group('dewpoint'))
    else:
        w.temperature = None

    # pressure
    pressure_re = re.compile(r"([QA])(\d+)")
    m = pressure_re.search(w.metar)
    if m and m.group(1) == 'A':
        # convert inHg to hPa
        w.pressure = round(float(m.group(2)) * 0.3386389)
    elif m:
        w.pressure = int(m.group(2))
    else:
        w.pressure = None

    return w


if __name__ == "__main__":
    import glob
    for station in glob.glob('test/metar/*.TXT'):
        with open(station) as f:
            print(parse(f.read()))
