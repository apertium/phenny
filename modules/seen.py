#!/usr/bin/env python
"""
seen.py - Phenny Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.
http://inamidst.com/phenny/
"""

import datetime
import logging
import os
import sqlite3
import time

logger = logging.getLogger('phenny')

def f_seen(phenny, input):
    """.seen <nick> - Reports when <nick> was last seen."""
    try:
        nick = str(input.group(2)).casefold()
    except UnboundLocalError:
        pass

    if nick == "none":
        phenny.reply(".seen <nick> - Reports when <nick> was last seen.")
        return
    try:
        seen_info = seen(nick, phenny)
    except NotSeenError:
        phenny.reply("Sorry, I haven't seen %s around." % str(input.group(2)))
        return

    t = time.strftime('%Y-%m-%d %H:%M:%S UTC', seen_info['at'].timetuple())
    msg = "I last saw %s at %s (%s) on %s" % (str(input.group(2)), t, seen_info['ago'], seen_info['channel'])
    phenny.reply(msg)

f_seen.name = 'seen'
f_seen.example = '.seen firespeaker'
f_seen.rule = (['seen'], r'(\S+)')

class NotSeenError(BaseException):
    pass

def seen(nick, phenny):
    '''seen(nick, phenny) returns dict of last seen for nick; 'ago' is a string describing how long ago; 'at' is datetime object in UTC; 'nick' is the nick; 'channel' is the last channel; raises NotSeenError when not seen.'''
    logger_conn = sqlite3.connect(phenny.logger_db, detect_types=sqlite3.PARSE_DECLTYPES)

    cNick = ""
    cChannel = ""
    c = logger_conn.cursor()
    c.execute("select * from lines_by_nick where nick = ? order by datetime(last_time) desc limit 1", (nick,))
    cl = c.fetchone()
    try:
        cNick = cl[1]
        cChannel = cl[0]
        cLastTime = cl[4]
    except TypeError:
        raise NotSeenError()
    c.close()

    if cNick != "":
        dt = timesince(cLastTime)
        t = cLastTime
    else:
        raise NotSeenError()

    return {'ago': dt, 'at': t, 'nick': cNick, 'channel': cChannel}

def timesince(td):
    seconds = int(abs(datetime.datetime.utcnow() - td).total_seconds())
    periods = [
        ('year', 60*60*24*365),
        ('month', 60*60*24*30),
        ('day', 60*60*24),
        ('hour', 60*60),
        ('minute', 60),
        ('second', 1)
    ]

    strings = []
    for period_name, period_seconds in periods:
            if seconds > period_seconds and len(strings) < 2:
                    period_value, seconds = divmod(seconds, period_seconds)
                    if period_value == 1:
                        strings.append("%s %s" % (period_value, period_name))
                    else:
                        strings.append("%s %ss" % (period_value, period_name))

    return "just now" if len(strings) < 1 else " and ".join(strings) + " ago"

if __name__ == '__main__':
        print(__doc__.strip())
