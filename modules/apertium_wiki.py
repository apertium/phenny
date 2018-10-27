#!/usr/bin/env python
"""
apertium_wiki.py - Phenny Wikipedia Module
"""

import re

from tools import truncate
from datetime import date, timedelta

import wiki
import web

endpoints = {
    'api': 'http://wiki.apertium.org/api.php?action=query&list=search&srlimit=1&format=json&srsearch={0}',
    'url': 'http://wiki.apertium.org/wiki/{0}',
    'log': 'https://tinodidriksen.com/pisg/freenode/logs/',
}


def apertium_wiki(phenny, origterm, to_nick=None):
    term, section = wiki.parse_term(origterm)

    w = wiki.Wiki(endpoints, None)
    match = w.search(term)

    if not match:
        phenny.say('Can\'t find anything in the Apertium Wiki for "{0}".'.format(term))
        return

    snippet, url = wiki.extract_snippet(match, section)

    if to_nick:
        phenny.say(truncate(snippet, to_nick + ', "{}" - ' + url))
    else:
        phenny.say(truncate(snippet, '"{}" - ' + url))


def awik(phenny, input):
    """Search for something on Apertium wiki or
    point another user to a page on Apertium wiki (supports pointing)"""
    origterm = input.group(2)
    to_nick = input.group(3)

    if not origterm:
        return phenny.say('Perhaps you meant ".wik Zen"?')

    apertium_wiki(phenny, origterm, to_nick=to_nick)


awik.rule = r'\.(awik)\s(.*)'
awik.example = '.awik Begiak or .awik point nick Begiak or .awik Begiak -> nick' ' or nick: .awik Begiak'
awik.priority = 'high'
awik.point = True


def awik2(phenny, input):
    nick, _, __, lang, origterm = input.groups()
    apertium_wiki(phenny, origterm, nick)


awik2.rule = r'(\S*)(:|,)\s\.(awik)(\.[a-z]{2,3})?\s(.*)'
awik2.example = 'svineet: .awik Begiak'
awik2.priority = 'high'


def logs(phenny, input):
    """Shows logs URL. """
    date_query = input.group(1)

    if date_query:
        date_query = date_query.replace(" ","").lower()

    endpoints['log'] += "%23" + phenny.channels[0][1:] + "/"

    if not date_query:
        phenny.say("Logs at %s" % endpoints['log'])
    elif "today" in date_query:
        today = str(date.today())
        phenny.say("Log at %s%s.log" % (endpoints['log'], today))
    elif "yesterday" in date_query:
        yesterday = str(date.today() - timedelta(1))
        phenny.say("Log at %s%s.log" % (endpoints['log'], yesterday))
    elif "last" in date_query:
        days = {"lastsunday": 0, "lastmonday": 1, "lasttuesday": 2,
                "lastwednesday": 3, "lastthursday": 4, "lastfriday": 5, "lastsaturday": 6}
        last_week = [today + timedelta(days=i)
                     for i in range(-8 - date.today().weekday(), date.today().weekday()-1)]
        day = str(last_week[days[date_query]])
        phenny.say("Log at %s%s.log" % (endpoints['log'], day))
    elif date_query.count("/") == 2 and len(date_query) == 10:
        month, day, year = date_query.split("/")
        month, day, year = int(month), int(day), int(year)
        if day in range(32) and month in range(13):
            day_query = str(date(year, month, day))
            if day_query in web.get("%s%s.log", endpoints['log'], day_query):
                phenny.say("Log at %s%s.log" % (endpoints['log'], day_query))
            else:
                phenny.say("I didn't understand that. Please use a date in the form MM/DD/YYYY.")
        else:
            phenny.say("I didn't understand that. Please use a date in the form MM/DD/YYYY.")
    else:
        phenny.say("I didn't understand that. Please use a date in the form MM/DD/YYYY.")


logs.commands = ['logs', 'log']
logs.priority = 'low'
logs.example = '.logs, .logs last wednesday, .logs 10/12/2018'
