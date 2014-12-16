#!/usr/bin/env python
"""
clock.py - Phenny Clock Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import os
import re
import math
import time
import locale
import socket
import struct
import datetime
import web
from bs4 import BeautifulSoup
from urllib.request import urlopen
from decimal import Decimal as dec
from tools import deprecated

TimeZones = {'KST': 9, 'CADT': 10.5, 'EETDST': 3, 'MESZ': 2, 'WADT': 9, 
                 'EET': 2, 'MST': -7, 'WAST': 8, 'IST': 5.5, 'B': 2, 
                 'MSK': 3, 'X': -11, 'MSD': 4, 'CETDST': 2, 'AST': -4, 
                 'HKT': 8, 'JST': 9, 'CAST': 9.5, 'CET': 1, 'CEST': 2, 
                 'EEST': 3, 'EAST': 10, 'METDST': 2, 'MDT': -6, 'A': 1, 
                 'UTC': 0, 'ADT': -3, 'EST': -5, 'E': 5, 'D': 4, 'G': 7, 
                 'F': 6, 'I': 9, 'H': 8, 'K': 10, 'PDT': -7, 'M': 12, 
                 'L': 11, 'O': -2, 'MEST': 2, 'Q': -4, 'P': -3, 'S': -6, 
                 'R': -5, 'U': -8, 'T': -7, 'W': -10, 'WET': 0, 'Y': -12, 
                 'CST': -6, 'EADT': 11, 'Z': 0, 'GMT': 0, 'WETDST': 1, 
                 'C': 3, 'WEST': 1, 'CDT': -5, 'MET': 1, 'N': -1, 'V': -9, 
                 'EDT': -4, 'UT': 0, 'PST': -8, 'MEZ': 1, 'BST': 1, 
                 'ACS': 9.5, 'ATL': -4, 'ALA': -9, 'HAW': -10, 'AKDT': -8, 
                 'AKST': -9, 
                 'BDST': 2, 'KGT': 6}

TZ1 = {
 'NDT': -2.5, 
 'BRST': -2, 
 'ADT': -3, 
 'EDT': -4, 
 'CDT': -5, 
 'MDT': -6, 
 'PDT': -7, 
 'YDT': -8, 
 'HDT': -9, 
 'BST': 1, 
 'MEST': 2, 
 'SST': 2, 
 'FST': 2, 
 'CEST': 2, 
 'EEST': 3, 
 'WADT': 8, 
 'KDT': 10, 
 'EADT': 13, 
 'NZD': 13, 
 'NZDT': 13, 
 'GMT': 0, 
 'UT': 0, 
 'UTC': 0, 
 'WET': 0, 
 'WAT': -1, 
 'AT': -2, 
 'FNT': -2, 
 'BRT': -3, 
 'MNT': -4, 
 'EWT': -4, 
 'AST': -4, 
 'EST': -5, 
 'ACT': -5, 
 'CST': -6, 
 'MST': -7, 
 'PST': -8, 
 'YST': -9, 
 'HST': -10, 
 'CAT': -10, 
 'AHST': -10, 
 'NT': -11, 
 'IDLW': -12, 
 'CET': 1, 
 'MEZ': 1, 
 'ECT': 1, 
 'MET': 1, 
 'MEWT': 1, 
 'SWT': 1, 
 'SET': 1, 
 'FWT': 1, 
 'EET': 2, 
 'UKR': 2, 
 'BT': 3, 
 'ZP4': 4, 
 'ZP5': 5, 
 'ZP6': 6, 
 'WST': 8, 
 'HKT': 8, 
 'CCT': 8, 
 'JST': 9, 
 'KST': 9, 
 'EAST': 10, 
 'GST': 10, 
 'NZT': 12, 
 'NZST': 12, 
 'IDLE': 12
}

TZ2 = {
 'ACDT': 10.5, 
 'ACST': 9.5, 
 'ADT': 3, 
 'AEDT': 11, # hmm
 'AEST': 10, # hmm
 'AHDT': 9, 
 'AHST': 10, 
 'AST': 4, 
 'AT': 2, 
 'AWDT': -9, 
 'AWST': -8, 
 'BAT': -3, 
 'BDST': -2, 
 'BET': 11, 
 'BST': -1, 
 'BT': -3, 
 'BZT2': 3, 
 'CADT': -10.5, 
 'CAST': -9.5, 
 'CAT': 10, 
 'CCT': -8, 
 # 'CDT': 5, 
 'CED': -2, 
 'CET': -1, 
 'CST': 6, 
 'EAST': -10, 
 # 'EDT': 4, 
 'EED': -3, 
 'EET': -2, 
 'EEST': -3, 
 'EST': 5, 
 'FST': -2, 
 'FWT': -1, 
 'GMT': 0, 
 'GST': -10, 
 'HDT': 9, 
 'HST': 10, 
 'IDLE': -12, 
 'IDLW': 12, 
 # 'IST': -5.5, 
 'IT': -3.5, 
 'JST': -9, 
 'JT': -7, 
 'KST': -9, 
 'MDT': 6, 
 'MED': -2, 
 'MET': -1, 
 'MEST': -2, 
 'MEWT': -1, 
 'MST': 7, 
 'MT': -8, 
 'NDT': 2.5, 
 'NFT': 3.5, 
 'NT': 11, 
 'NST': -6.5, 
 'NZ': -11, 
 'NZST': -12, 
 'NZDT': -13, 
 'NZT': -12, 
 # 'PDT': 7, 
 'PST': 8, 
 'ROK': -9, 
 'SAD': -10, 
 'SAST': -9, 
 'SAT': -9, 
 'SDT': -10, 
 'SST': -2, 
 'SWT': -1, 
 'USZ3': -4, 
 'USZ4': -5, 
 'USZ5': -6, 
 'USZ6': -7, 
 'UT': 0, 
 'UTC': 0, 
 'UZ10': -11, 
 'WAT': 1, 
 'WET': 0, 
 'WST': -8, 
 'YDT': 8, 
 'YST': 9, 
 'ZP4': -4, 
 'ZP5': -5, 
 'ZP6': -6
}

TZ3 = {
    'AEST': 10, 
    'AEDT': 11
}

# TimeZones.update(TZ2) # do these have to be negated?
TimeZones.update(TZ1)
TimeZones.update(TZ3)

r_local = re.compile(r'\([a-z]+_[A-Z]+\)')

def stripHtmlTags(htmlTxt):
    if htmlTxt is None:
        return None
    else:
        return ''.join(htmlTxt.findAll(text=True))

def GetTime(phenny):
    """Returns a data of timezones"""
    data = {}
    addr=urlopen('http://24timezones.com/current_time_zone.php').read()
    soup=BeautifulSoup(addr)
    table=soup.find('table')
    getTime=False
    errNo=False
    phenny.reply('Updating a database..')
    for tds in table.find_all('td'):
        if getTime==True:
            ctu=stripHtmlTags(tds)
            data[ctz]=ctu
            print(data[ctz]+' | '+ctz)
            getTime=False
        elif getTime==False:
            ctz=stripHtmlTags(tds)
            getTime=True
    return data

def write_TZBase(filename, data):
    with open(filename, 'w', encoding="utf-16") as f:
        for k, v in data.items():
            f.write('{}${}\n'.format(k, v))

def read_TZBase(filename):
    data = {}
    with open(filename, 'r', encoding="utf-16") as f:
        for line in f.readlines():
            if line == '\n':
                continue
            code, name = line.replace('\n', '').split('$')
            data[code] = name
    return data

def Prepare(phenny):
    name = 'tz_data.db'
    f1 = os.path.join(os.path.expanduser('~/.phenny'), name)
    if os.path.exists(f1):
        try:
            data = read_TZBase(f1)
            return True
        except ValueError:
            print('time zones database read failed, refreshing it')
            write_TZBase(f1, GetTime(phenny))
            data = read_TZBase(f1)
            return True
    else:
        print('time zones database has not found, please use .tz function for getting it')
        return False

def refresh_TZdatabase(phenny, raw=None):
    if raw.admin or raw is None:
        name = 'tz_data.db'
        f1 = os.path.join(os.path.expanduser('~/.phenny'), name)
        write_TZBase(f1, GetTime(phenny))
        phenny.say('Time zones database has updated!')
    else:
        phenny.say('Only admins can execute that command!')
refresh_TZdatabase.name='tz'
refresh_TZdatabase.commands = ['tz']
refresh_TZdatabase.example = '.tz'

def GetTimeFromData(phenny, input):
    if Prepare(phenny)==False:
        return False
    else:
        name = 'tz_data.db'
        f1 = os.path.join(os.path.expanduser('~/.phenny'), name)
        data = read_TZBase(f1)
        for (slug, title) in data.items():
            if slug == input.group(2):
                phenny.reply(title+' in '+slug)
                return True
    return False


def f_time(phenny, input): 
    """Returns the current time."""
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
    if len(tz) > 30: return

    if (TZ == 'UTC') or (TZ == 'Z'): 
        msg = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        phenny.reply(msg)
    elif r_local.match(tz): # thanks to Mark Shoulsdon (clsn)
        locale.setlocale(locale.LC_TIME, (tz[1:-1], 'UTF-8'))
        msg = time.strftime("%A, %d %B %Y %H:%M:%SZ", time.gmtime())
        phenny.reply(msg)
    elif TZ in TimeZones: 
        offset = TimeZones[TZ] * 3600
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
                if GetTimeFromData(phenny, input)==False:
                    error = "Sorry, I don't know about the '%s' timezone." % tz
                    phenny.reply(error)
        else: 
            timenow = time.gmtime(time.time() + (t * 3600))
            msg = time.strftime("%a, %d %b %Y %H:%M:%S " + str(tz), timenow)
            phenny.reply(msg)
f_time.name = 'time'
f_time.commands = ['time']
f_time.example = '.time UTC'

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
