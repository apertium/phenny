#!/usr/bin/env python
"""
remind.py - Phenny Reminder Module
Copyright 2011, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import threading
import time
from modules import clock
from tools import read_db, write_db

def load_database(phenny):
    return read_db(phenny, 'reminders')

def dump_database(phenny):
    write_db(phenny, 'reminders', phenny.remind_data)

def setup(phenny): 
    phenny.remind_data = load_database(phenny)

    def monitor(phenny): 
        time.sleep(5)
        while True: 
            now = int(time.time())
            unixtimes = [int(key) for key in phenny.remind_data]
            oldtimes = [t for t in unixtimes if t <= now]
            if oldtimes: 
                for oldtime in oldtimes: 
                    for (channel, nick, message) in phenny.remind_data[oldtime]:
                        if message: 
                            phenny.msg(channel, nick + ': ' + message)
                        else: phenny.msg(channel, nick + '!')
                    del phenny.remind_data[oldtime]
                dump_database(phenny)
            time.sleep(2.5)

    targs = (phenny,)
    t = threading.Thread(target=monitor, args=targs)
    t.daemon = True
    t.start()

scaling = {
    'years': 365.25 * 24 * 3600, 
    'year': 365.25 * 24 * 3600, 
    'yrs': 365.25 * 24 * 3600, 
    'y': 365.25 * 24 * 3600, 

    'months': 29.53059 * 24 * 3600, 
    'month': 29.53059 * 24 * 3600, 
    'mo': 29.53059 * 24 * 3600, 

    'weeks': 7 * 24 * 3600, 
    'week': 7 * 24 * 3600, 
    'wks': 7 * 24 * 3600, 
    'wk': 7 * 24 * 3600, 
    'w': 7 * 24 * 3600, 

    'days': 24 * 3600, 
    'day': 24 * 3600, 
    'd': 24 * 3600, 

    'hours': 3600, 
    'hour': 3600, 
    'hrs': 3600, 
    'hr': 3600, 
    'h': 3600, 

    'minutes': 60, 
    'minute': 60, 
    'mins': 60, 
    'min': 60, 
    'm': 60, 

    'seconds': 1, 
    'second': 1, 
    'secs': 1, 
    'sec': 1, 
    's': 1
}

periods = '|'.join(list(scaling.keys()))
p_command = r'\.in ([0-9]+(?:\.[0-9]+)?)\s?((?:%s)\b)?:?\s?(.*)' % periods
r_command = re.compile(p_command)

def remind(phenny, input): 
    """Set a reminder"""
    m = r_command.match(input.bytes)
    if not m: 
        return phenny.reply("Sorry, didn't understand the input.")
    length, scale, message = m.groups()

    length = float(length)
    factor = scaling.get(scale, 60)
    duration = length * factor

    if duration % 1: 
        duration = int(duration) + 1
    else: duration = int(duration)

    t = int(time.time()) + duration
    reminder = (input.sender, input.nick, message)

    try: phenny.remind_data[t].append(reminder)
    except KeyError: phenny.remind_data[t] = [reminder]

    dump_database(phenny)

    if duration >= 60: 
        w = ''
        if duration >= 3600 * 12: 
            w += time.strftime(' on %d %b %Y', time.gmtime(t))
        w += time.strftime(' at %H:%MZ', time.gmtime(t))
        phenny.reply('Okay, will remind%s' % w)
    else: phenny.reply('Okay, will remind in %s secs' % duration)
remind.name = 'in'
remind.example = 'in 15 minutes do work'
remind.commands = ['in']

r_time = re.compile(r'^([0-9]{2}[:.][0-9]{2})')
r_zone = re.compile(r'( ?([A-Za-z]+|[+-]\d\d?))')

import calendar

def at(phenny, input):
    message = input[4:]

    m = r_time.match(message)
    if not m: 
        return phenny.reply("Sorry, didn't understand the time spec.")
    t = m.group(1).replace('.', ':')
    message = message[len(t):]

    m = r_zone.match(message)
    if not m: 
        return phenny.reply("Sorry, didn't understand the zone spec.")
    z = m.group(2)
    message = message[len(m.group(1)):].strip()

    if z.startswith('+') or z.startswith('-'):
        tz = int(z)

    tz = clock.get_offsets(phenny, z)
    if not tz:
        return phenny.reply("Sorry, didn't understand the time zone.")
    tz = tz[0][1]

    d = time.strftime("%Y-%m-%d", time.gmtime())
    d = time.strptime(("%s %s" % (d, t)), "%Y-%m-%d %H:%M")

    d = int(calendar.timegm(d) - (3600 * tz))
    duration = int((d - time.time()) / 60)

    if duration < 1:
        return phenny.reply("Sorry, that date is this minute or in the past. And only times in the same day are supported!")

    # phenny.say("%s %s %s" % (t, tz, d))

    reminder = (input.sender, input.nick, message)
    # phenny.say(str((d, reminder)))
    try: phenny.remind_data[d].append(reminder)
    except KeyError: phenny.remind_data[d] = [reminder]

    phenny.sending.acquire()
    dump_database(phenny)
    phenny.sending.release()

    phenny.reply("Reminding at %s %s - in %s minute(s)" % (t, z, duration))
at.commands = ['at']

if __name__ == '__main__': 
    print(__doc__.strip())
