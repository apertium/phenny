#!/usr/bin/env python
"""
apertium_wiki.py - Phenny Wikipedia Module
"""


from tools import truncate

import datetime as dt

import wiki
import web

from bot import command

endpoints = {
    'api': 'https://wiki.apertium.org/api.php?action=query&list=search&srlimit=1&format=json&srsearch={0}',
    'url': 'https://wiki.apertium.org/wiki/{0}',
    'logs': 'https://tinodidriksen.com/pisg/OFTC/logs/',
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

@command('awik', priority='high', example='.awik Begiak or .awik Begiak -> nick or nick: .awik Begiak')
def awik(phenny, msg):
    """Search for something on Apertium wiki or
    point another user to a page on Apertium wiki (supports pointing)"""
    if not msg.command_args:
        phenny.say('Perhaps you meant ".wik Zen"?')
        return
    apertium_wiki(phenny, msg.command_args, to_nick=msg.command_point)

@command(['log', 'logs'], priority='low', example='.logs, .logs last wednesday, .logs 10/12/2018')
def logs(phenny, msg):
    """ Shows logs URL. """
    date_query = msg.command_args

    if date_query:
        date_query = date_query.lower().strip()

    endpoints['log'] = "{0}%23{1}/".format(endpoints['logs'], phenny.channels[0][1:])

    if not date_query:
        # .logs
        phenny.say("Log at {0}".format(endpoints['log']))
    elif "today" in date_query:
        # .logs today
        phenny.say("Log at {0}{1}.log".format(endpoints['log'], dt.date.today()))
    elif "yesterday" in date_query:
        # .logs yesterday
        yesterday = dt.date.today() - dt.timedelta(1)
        phenny.say("Log at {0}{1}.log".format(endpoints['log'], yesterday))
    elif "last" in date_query:
        # .logs last <day of week>
        days = {"sun": 0, "mon": 1, "tue": 2,
                "wed": 3, "thurs": 4, "fri": 5, "sat": 6}
        last_week = [dt.date.today() + dt.timedelta(days=i) for i in range(-8 - dt.date.today().weekday(), dt.date.today().weekday() - 1)]
        n = (days[i] for i in days.keys() if i in date_query)
        phenny.say("Log at {0}{1}.log".format(endpoints['log'], last_week[next(n)]))
    elif date_query.count("/") == 2 and len(date_query) == 10:
        # .logs MM/DD/YYYY
        try:
            day_query = dt.datetime.strftime(dt.datetime.strptime(date_query, "%m/%d/%Y"), "%Y-%m-%d")  # raises ValueError if not correct format
            if "***" in web.get("{0}{1}.log".format(endpoints['log'], day_query)):
                phenny.say("Log at {0}{1}.log".format(endpoints['log'], day_query))
            else:
                raise ValueError  # case in which date does not have log
        except ValueError:
            phenny.say("I didn't understand that. Please use a date in the form MM/DD/YYYY.")
