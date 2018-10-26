#!/usr/bin/env python
"""
apertium_wiki.py - Phenny Wikipedia Module
"""

import re

from tools import truncate
from datetime import date, timedelta

import wiki
import requests

endpoints = {
    'api': 'http://wiki.apertium.org/api.php?action=query&list=search&srlimit=1&format=json&srsearch={0}',
    'url': 'http://wiki.apertium.org/wiki/{0}',
    'log': 'https://tinodidriksen.com/pisg/freenode/logs/%23apertium/',
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
    date_q = input.group(1)
    if date_q:
        date_q = date_q.strip().lower()
    if not date_q:
        phenny.say("Logs at %s" % endpoints['log'])
    elif "today" in date_q:
        today = str(date.today())
        phenny.say("Log at %s" % endpoints['log']+today+".log")
    elif "yesterday" in date_q:
        yesterday = str(date.today() - timedelta(1))
        phenny.say("Log at %s" % endpoints['log']+yesterday+".log")
    elif "last" in date_q:
        date_q = date_q.replace("last ", "")
        days = {"sunday": 0, "monday": 1, "tuesday": 2,
                "wednesday": 3, "thursday": 4, "friday": 5, "saturday": 6}
        today = date.today()
        last_week = [today + timedelta(days=i)
                     for i in range(-8 - today.weekday(), today.weekday()-1)]
        req_day = str(last_week[days[date_q]])
        phenny.say("Log at %s" % endpoints['log']+req_day+".log")
    elif date_q.count("/") == 2 and len(date_q.strip()) == 10:
        date_q = date_q.strip().replace("/", "-")
        date_q = date_q[-4:] + "-" + date_q[:5]
        response = requests.get(endpoints['log']+date_q+".log")
        if response.status_code == "404":
            phenny.say(
                "I didn't understand that. Please use a date in the form xx/yy/zzzz, in which x is two digits for month, y is day, etc.")
        else:
            phenny.say("Log at %s" % endpoints['log']+date_q+".log")
    else:
        phenny.say(
            "I didn't understand that. Please use a date in the form xx/yy/zzzz, in which x is two digits for month, y is day, etc.")


logs.commands = ['logs', 'log']
logs.priority = 'low'
logs.example = '.logs, .logs last wednesday, .logs 10/12/2018'
