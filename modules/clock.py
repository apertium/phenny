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
from lxml import html
from decimal import Decimal as dec
from tools import deprecated

r_local = re.compile(r'\([a-z]+_[A-Z]+\)')

def f_time(phenny, input): 
    """.time [timezone] - Show current time in defined timezone. Defaults to GMT."""
    tz = input.group(2) or 'GMT'

    # Personal time zones, because they're rad
    if hasattr(phenny.config, 'timezones'): 
        People = phenny.config.timezones
    else: People = {}

    if tz in People: 
        tz = People[tz]
    elif (not input.group(2)) and input.nick in People: 
        tz = People[input.nick]

    TZ = tz.upper()
    longs=int(len(tz))
    if len(tz) > 30: return
    for (slug, title) in phenny.tz_data.items():
        if slug[:longs]==TZ:
            offset = phenny.tz_data[slug] * 3600
            timenow = time.gmtime(time.time() + offset)
            msg = time.strftime("%a, %d %b %Y %H:%M:%S " + str(slug), timenow)
            phenny.reply(msg)
            skip=True
            break
    if skip ==False:
        if (TZ == 'UTC') or (TZ == 'Z'): 
            msg = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            phenny.reply(msg)
        elif r_local.match(tz): # thanks to Mark Shoulsdon (clsn)
            locale.setlocale(locale.LC_TIME, (tz[1:-1], 'UTF-8'))
            msg = time.strftime("%A, %d %B %Y %H:%M:%SZ", time.gmtime())
            phenny.reply(msg)
        elif TZ in phenny.tz_data: 
            if skip==False:
                offset = phenny.tz_data[TZ] * 3600
                timenow = time.gmtime(time.time() + offset)
                msg = time.strftime("%a, %d %b %Y %H:%M:%S " + str(TZ), timenow)
                phenny.reply(msg)
        elif tz and tz[0] in ('+', '-') and 4 <= len(tz) <= 6: 
            timenow = time.gmtime(time.time() + (int(tz[:3]) * 3600))
            msg = time.strftime("%a, %d %b %Y %H:%M:%S " + str(tz), timenow)
            phenny.reply(msg)
        else: 
            try: t = float(tz)
            except ValueError: 
                import os, re, subprocess
                r_tz = re.compile(r'^[A-Za-z]+(?:/[A-Za-z_]+)*$')
                if r_tz.match(tz) and os.path.isfile('/usr/share/zoneinfo/' + tz): 
                    cmd, PIPE = 'TZ=%s date' % tz, subprocess.PIPE
                    proc = subprocess.Popen(cmd, shell=True, stdout=PIPE)
                    phenny.reply(proc.communicate()[0])
                else: 
                    error = "Sorry, I don't know about the '%s' timezone." % tz
                    phenny.reply(error)
            else: 
                timenow = time.gmtime(time.time() + (t * 3600))
                msg = time.strftime("%a, %d %b %Y %H:%M:%S " + str(tz), timenow)
                phenny.reply(msg)
f_time.name = 'time'
f_time.commands = ['time']
f_time.example = '.time UTC'

def scrape_wiki_zones():
    data = {}
    url = 'http://en.wikipedia.org/wiki/List_of_time_zone_abbreviations'
    resp = web.get(url)
    h = html.document_fromstring(resp)
    table = h.find_class('wikitable')[0]
    for row in table.findall('tr')[1:]:
        code = row.findall('td')[0].text
        offset = row.findall('td')[2].find('a').text[3:]
        offset = offset.replace('−', '-') # replacing minus sign with hyphen
        if offset.find(':') > 0:
            offset = int(offset.split(':')[0]) + int(offset.split(':')[1]) / 60
        else:
            if offset == '':
                offset = 0
            offset = int(offset)
        data[code] = offset
    url = 'http://en.wikipedia.org/wiki/List_of_tz_database_time_zones'
    resp = web.get(url)
    h = html.document_fromstring(resp)
    table = h.find_class('wikitable')[0]
    for trs in table.findall('tr'):
        tmr=0
        for tds in trs.findall('td'):
            tmr=tmr+1
            if tmr==3:
                ctz=tds.find('a').text[tds.find('a').text.find('/')+1:].replace('_',' ')
                if ctz.find('/')!=-1:
                    ctz=ctz[ctz.find('/')+1:]
            if tmr==5:
                ctu=tds.find('a').text
                if ctu[ctu.find(':')+1]=='0':
                    ctu=ctu[:ctu.find(':')]
                else:
                    ctu=ctu[:ctu.find(':')]+'.5'
                if ctu[0]=='−':
                    ctu='-'+ctu[1:]
                data[ctz.upper()]=float(ctu)
    return data

def filename(phenny):
    name = phenny.nick + '-' + phenny.config.host + '.timezones.db'
    return os.path.join(os.path.expanduser('~/.phenny'), name)

def write_dict(filename, data):
    with open(filename, 'w') as f:
        for k, v in data.items():
            f.write('{}${}\n'.format(k, v))

def read_dict(filename):
    data = {}
    with open(filename, 'r') as f:
        for line in f.readlines():
            if line == '\n':
                continue
            code, offset = line.replace('\n', '').split('$')
            if offset.find('.') == -1:
                offset = int(offset)
            else:
                offset = float(offset)
            data[code] = offset
    return data

def refresh_database_tz(phenny, raw=None):
    if raw.admin or raw is None:
        f = filename(phenny)
        phenny.tz_data = scrape_wiki_zones()
        write_dict(f, phenny.tz_data)
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
thread_check_tz.name = 'tzst'
thread_check_tz.commands = ['tzdb status']

def setup(phenny):
    f = filename(phenny)
    if os.path.exists(f):
        try:
            phenny.tz_data = read_dict(f)
        except ValueError:
            print('timezone database read failed, refreshing it')
            phenny.tz_data = scrape_wiki_zones()
            write_dict(f, phenny.tz_data)
    else:
        phenny.tz_data = scrape_wiki_zones()
        write_dict(f, phenny.tz_data)

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

if __name__ == '__main__': 
    print(__doc__.strip())
