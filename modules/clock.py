#!/usr/bin/env python
"""
clock.py - Phenny Clock Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import math
import time
import locale
import socket
import struct
import datetime
import web
import os
import threading
import csv
import logging
import subprocess
from lxml import html
from decimal import Decimal as dec
from tools import deprecated, GrumbleError, read_db, write_db

logger = logging.getLogger('phenny')

r_local = re.compile(r'\([a-z]+_[A-Z]+\)')


def get_offsets(phenny, key):
    offsets = []

    if key in phenny.time_zone_abbreviations:
        offsets.extend(phenny.time_zone_abbreviations[key])

    for (name, offset) in phenny.tz_database_time_zones.items():
        if len(name) >= len(key) and name[:len(key)] == key:
            offsets.append((name, offset))

    return offsets

def give_time(phenny, tz, input_nick, to_user=None):
    if "->" in tz: return
    if "→" in tz: return

    tz_complete = tz.upper()

    math_add = 0
    if '+' in tz or '-' in tz:
        zone_and_add = tz.split('+') if '+' in tz else tz.split('-')
        to_add = zone_and_add[1]
        if ':' in to_add:
            parts = to_add.split(':')
            if len(parts[1]) > 2:
                phenny.reply('Minutes to add allowed only upto 59. Please convert to hours if you want more.')
                return
            if int(parts[1]) > 59:
                phenny.reply('Minutes to add allowed only upto 59. Please convert to hours if you want more.')
                return
            if len(parts[0]) > 2:
                phenny.reply('Time to add allowed only upto 24 hours.')
                return
            if int(parts[0]) > 24:
                phenny.reply('Time to add allowed only upto 24 hours.')
                return
            if int(parts[0]) == 24 and int(parts[1]) > 0:
                phenny.reply('Time to add allowed only upto 24 hours.')
                return
            math_add = int(parts[0]) * 3600 + int(parts[1]) * 60
        else:
            if len(to_add) > 2:
                phenny.reply('Time to add allowed only upto 24 hours.')
                return
            if int(to_add) > 24:
                phenny.reply('Time to add allowed only upto 24 hours.')
                return
            math_add = int(to_add) * 3600
        if '-' in tz:
            math_add *= -1
        tz = zone_and_add[0]

    try:
        read_wiki_zones(phenny)
    except:
        logger.warning('timezone database read failed, update it')

    # Personal time zones, because they're rad
    if hasattr(phenny.config, 'timezones'):
        People = phenny.config.timezones
    else: People = {}

    if tz in People:
        tz = People[tz]
    elif (not tz) and input_nick in People:
        tz = People[input_nick]

    if len(tz) > 30: return

    TZ = tz.upper()
    tz_offsets = get_offsets(phenny, TZ)

    if tz_offsets:
        msgs = []

        for tz_offset in tz_offsets[:3]:
            offset = tz_offset[1] * 3600 + math_add
            timenow = time.gmtime(time.time() + offset)
            msgs.append(tz_offset[0] + ': ' + time.strftime("%a, %d %b %Y %H:%M:%S", timenow))

        msg = '; '.join(msgs)

        if to_user:
            phenny.say(to_user + ', ' + msg)
        else:
            phenny.reply(msg)

        if len(tz_offsets) > 3:
            msg = 'Found ' + str(len(tz_offsets)) + ' more matching timezones.'

            if to_user:
                phenny.say(to_user + ', ' + msg)
            else:
                phenny.reply(msg)

        return

    if (TZ == 'UTC') or (TZ == 'Z'):
        msg = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        if to_user:
            phenny.say(to_user+', '+msg)
        else:
            phenny.reply(msg)
    elif r_local.match(tz): # thanks to Mark Shoulsdon (clsn)
        locale.setlocale(locale.LC_TIME, (tz[1:-1], 'UTF-8'))
        msg = time.strftime("%A, %d %B %Y %H:%M:%SZ", time.gmtime())

        if to_user:
            phenny.say(to_user+', '+msg)
        else:
            phenny.reply(msg)
    elif tz and tz[0] in ('+', '-') and 4 <= len(tz) <= 6:
        timenow = time.gmtime(time.time() + (int(tz[:3]) * 3600))
        msg = time.strftime("%a, %d %b %Y %H:%M:%S " + tz_complete, timenow)

        if to_user:
            phenny.say(to_user+', '+msg)
        else:
            phenny.reply(msg)
    else:
        try:
            t = float(tz)
        except ValueError:
            r_tz = re.compile(r'^[A-Za-z]+(?:/[A-Za-z_]+)*$')

            if r_tz.match(tz) and os.path.isfile('/usr/share/zoneinfo/' + tz):
                cmd, PIPE = 'TZ=%s date' % tz, subprocess.PIPE
                proc = subprocess.Popen(cmd, shell=True, stdout=PIPE)

                if to_user:
                    phenny.say(to_user+', '+proc.communicate()[0])
                else:
                    phenny.reply(proc.communicate()[0])
            else:
                # error = "Sorry, I don't know about the '%s' timezone. Suggest the city on http://www.citytimezones.info" % tz
                error = "Sorry, I don't know about the '%s' timezone." % tz
                phenny.reply(error)
        else:
            timenow = time.gmtime(time.time() + (t * 3600))
            msg = time.strftime("%a, %d %b %Y %H:%M:%S " + tz_complete, timenow)

            if to_user:
                phenny.say(to_user+', '+msg)
            else:
                phenny.reply(msg)

def f_time(phenny, input):
    """.time [timezone] - Show current time in defined timezone. Defaults to GMT. (supports pointing)"""
    tz = input.group(2) or 'GMT'

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(tz)
    if matched_point:
        to_nick = matched_point.groups()[0]
        tz2 = matched_point.groups()[1]

        give_time(phenny, tz2, input.nick, to_user=to_nick)
        return

    give_time(phenny, tz, input.nick)

f_time.name = 'time'
f_time.commands = ['time']
f_time.example = '.time UTC or .time point nick GMT or nick: .time GMT or '+\
                 '.time GMT -> nick'


def f_time2(phenny, input):
    nick, _, __, tz = input.groups()

    give_time(phenny, tz, input.nick, to_user=nick)

f_time2.rule = r'(\S*)(:|,)\s\.(time)\s(.*)'


def f_time3(phenny, input):
    _, __, nick = input.groups()

    give_time(phenny, "", input.nick, to_user=nick)

f_time3.rule = r'\.(time)\s(->|→)\s(\S*)'


def f_time4(phenny, input):
    _, tz, __, nick = input.groups()

    give_time(phenny, tz, input.nick, to_user=nick)

f_time4.rule = r'\.(time)\s(.*)\s(->|→)\s(\S*)'


def f_time5(phenny, input):
    nick, _, __ = input.groups()

    give_time(phenny, "", input.nick, to_user=nick)

f_time5.rule = r'(\S*)(:|,)\s\.(time)$'


def scrape_wiki_time_zone_abbreviations():
    data = {}

    url = 'http://en.wikipedia.org/wiki/List_of_time_zone_abbreviations'
    doc = html.document_fromstring(web.get(url))
    table = doc.find_class('wikitable')[0]
    rows = table.findall('tr')

    column_names = [cell.text_content() for cell in rows[0].findall('th')]

    for row in rows[1:]:
        column = 0

        for cell in row.findall('td'):
            if column == column_names.index('Abbr.'):
                code = cell.text
            elif column == column_names.index('Name'):
                name = cell.find('a').text
            elif column == column_names.index('UTC offset'):
                offset = cell.find('a').text[3:]
                offset = offset.replace('−', '-') # hyphen -> minus

                if offset.find(':') > 0:
                    parts = offset.split(':')
                    offset = int(parts[0]) + int(parts[1]) / 60
                else:
                    if offset == '':
                        offset = 0

                    offset = offset.strip('±') # ±00 -> 00
                    offset = int(offset)

            column += 1

        datapoint = (name, offset)

        if code in data:
            data[code].append(datapoint)
        else:
            data[code] = [datapoint]

    return data


def scrape_wiki_tz_database_time_zones():
    data = {}

    url = 'http://en.wikipedia.org/wiki/List_of_tz_database_time_zones'
    doc = html.document_fromstring(web.get(url))
    table = doc.find_class('wikitable')[0]
    rows = table.findall('tr')

    column_names = [cell.text_content().replace('*', '') for cell in rows[0].findall('th')]

    for row in rows[1:]:
        column = 0

        for cell in row.findall('td'):
            if column == column_names.index('TZ'):
                text = cell.find('a').text
                text = text.replace('_', ' ').replace('−', '-')

                name = text.split('/')[-1]
            elif column == column_names.index('UTC offset'):
                text = cell.find('a').text
                text = text.replace('_', ' ').replace('−', '-')

                if text[text.find(':') + 1] == '0':
                    text = text[:text.find(':')]
                else:
                    text = text[:text.find(':')] + '.5'

            column += 1

        if '+' in name or '-' in name:
            continue

        data[name.upper()] = float(text)

    return data

def scrape_wiki_zones(phenny):
    phenny.time_zone_abbreviations = scrape_wiki_time_zone_abbreviations()
    phenny.tz_database_time_zones = scrape_wiki_tz_database_time_zones()

def write_wiki_zones(phenny):
    write_db(phenny, 'tz_abbr', phenny.time_zone_abbreviations)
    write_db(phenny, 'tz_db', phenny.tz_database_time_zones)

def read_wiki_zones(phenny):
    thirty_days = 30*24*60*60
    phenny.time_zone_abbreviations = read_db(phenny, 'tz_abbr', warn_after=thirty_days)
    phenny.tz_database_time_zones = read_db(phenny, 'tz_db', warn_after=thirty_days)

def refresh_database_tz(phenny, raw=None):
    if raw.admin or raw is None:
        rescrape_wiki_tz(phenny)
        phenny.say('Timezone database successfully written')
    else:
        phenny.say('Only admins can execute that command!')
refresh_database_tz.name = 'refresh_timezone_database'
refresh_database_tz.commands = ['tzdb update']
refresh_database_tz.thread = True

def thread_check_tz(phenny, raw):
    for t in threading.enumerate():
        if t.name == refresh_database_tz.name:
            phenny.say('A timezone updating thread is currently running')
            break
    else:
        phenny.say('No timezone updating thread running')
thread_check_tz.name = 'timezone_thread_check'
thread_check_tz.commands = ['tzdb status']

def setup(phenny):
    try:
        read_wiki_zones(phenny)
    except (GrumbleError, ResourceWarning):
        logger.debug('timezone database read failed, refreshing it')
        scrape_wiki_zones(phenny)
        write_wiki_zones(phenny)

def beats(phenny, input):
    """Shows the internet time in Swatch beats."""
    beats = ((time.time() + 3600) % 86400) / 86.4
    beats = int(math.floor(beats))
    phenny.say('@%03i' % beats)
beats.commands = ['beats']
beats.priority = 'low'

def divide(input, by):
    return (input // by), (input % by)

def yi(phenny, input):
    """Shows whether it is currently yi or not."""
    quadraels, remainder = divide(int(time.time()), 1753200)
    raels = quadraels * 4
    extraraels, remainder = divide(remainder, 432000)
    if extraraels == 4:
        return phenny.say('Yes! PARTAI!')
    elif extraraels == 3:
          return phenny.say('Soon...')
    else: phenny.say('Not yet...')
yi.commands = ['yi']
yi.priority = 'low'

def tock(phenny, input):
    """Shows the time from the USNO's atomic clock."""
    info = web.head('http://tycho.usno.navy.mil/cgi-bin/timer.pl')
    phenny.say('"' + info['Date'] + '" - tycho.usno.navy.mil')
tock.commands = ['tock']
tock.priority = 'high'

def npl(phenny, input):
    """Shows the time from NPL's SNTP server."""
    # for server in ('ntp1.npl.co.uk', 'ntp2.npl.co.uk'):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(b'\x1b' + 47 * b'\0', ('ntp1.npl.co.uk', 123))
    data, address = client.recvfrom(1024)
    if data:
        buf = struct.unpack('B' * 48, data)
        d = dec('0.0')
        for i in range(8):
            d += dec(buf[32 + i]) * dec(str(math.pow(2, (3 - i) * 8)))
        d -= dec(2208988800)
        a, b = str(d).split('.')
        f = '%Y-%m-%d %H:%M:%S'
        result = datetime.datetime.fromtimestamp(d).strftime(f) + '.' + b[:6]
        phenny.say(result + ' - ntp1.npl.co.uk')
    else: phenny.say('No data received, sorry')
npl.commands = ['npl']
npl.priority = 'high'


def time_zone_convert(phenny, input_txt, to_user=None):
    format_regex = re.compile("(\d*)([a-zA-Z\s,-]*)\sin\s([a-zA-z\s]*)")
    if not input_txt:
        phenny.reply(tz.__doc__.strip())
        return
    regex_match = format_regex.search(input_txt)
    if (not regex_match) or (regex_match.groups()[0] == "") or (regex_match.groups()[1] == "") or (regex_match.groups()[2] == ""):
        phenny.reply(tz.__doc__.strip())
    else:
        from_tz_match = get_offsets(phenny, regex_match.groups()[1].upper())
        to_tz_match = get_offsets(phenny, regex_match.groups()[2].upper())

        from_tz_match = from_tz_match[0][1] if from_tz_match else ""
        to_tz_match = to_tz_match[0][1] if to_tz_match else ""

        if (from_tz_match == "") or (to_tz_match == ""):
            if (from_tz_match == "") or (to_tz_match == ""):
                phenny.reply("Please enter valid time zone(s) :P")
                return

        time_hours = int(int(regex_match.groups()[0])/100)
        time_mins = int(regex_match.groups()[0])%100
        if (time_hours >= 24) or (time_hours < 0) or (time_mins >= 60) or (time_mins < 0):
            phenny.reply("Please enter a valid time :P")
            return
        time_diff_hours = int(to_tz_match-from_tz_match)
        time_diff_minutes = int(((to_tz_match-from_tz_match)-time_diff_hours)*60)

        dest_time_hours = time_hours + time_diff_hours
        dest_time_mins = time_mins + time_diff_minutes

        if dest_time_mins >= 60:
            dest_time_mins = dest_time_mins - 60
            dest_time_hours = dest_time_hours + 1
        elif dest_time_mins < 0:
            dest_time_mins = dest_time_mins + 60
            dest_time_hours = dest_time_hours - 1

        if dest_time_hours >= 24:
            dest_time_hours = dest_time_hours - 24
        elif dest_time_hours < 0:
            dest_time_hours = dest_time_hours + 24

        if to_user:
            phenny.say(to_user + ', ' +
                       format(dest_time_hours, '02d') +
                       format(dest_time_mins, '02d') +
                       regex_match.groups()[2].upper())
        else:
            phenny.reply(format(dest_time_hours, '02d') +
                         format(dest_time_mins, '02d') +
                         regex_match.groups()[2].upper())

def tz(phenny, input):
    """Usage: .tz <time><from timezone> in <destination> - Convert time to destination zone. (supports pointing)"""

    input_txt = input.group(2)
    if not input_txt:
        phenny.reply(tz.__doc__.strip())
        return

    if "->" in input_txt: return
    if "→" in input_txt: return

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(input_txt)
    if matched_point:
        to_nick = matched_point.groups()[0]
        input_txt2 = matched_point.groups()[1]

        time_zone_convert(phenny, input_txt2, to_user=to_nick)
        return

    time_zone_convert(phenny, input_txt)


tz.commands = ['tz']
tz.priority = 'high'


def time_zone2(phenny, input):
    _, input_txt, __, nick = input.groups()

    time_zone_convert(phenny, input_txt, to_user=nick)

time_zone2.rule = r'\.(tz)\s(.*)\s(->|→)\s(\S*)'


def time_zone3(phenny, input):
    nick, _, __, input_txt = input.groups()

    time_zone_convert(phenny, input_txt, to_user=nick)

time_zone3.rule = r'(\S*)(:|,)\s\.(tz)\s(.*)'

if __name__ == '__main__':
    print(__doc__.strip())
