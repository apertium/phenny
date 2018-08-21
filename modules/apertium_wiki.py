#!/usr/bin/env python
"""
apertium_wiki.py - Phenny Wikipedia Module
"""

import re

from tools import truncate
import wiki

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
    """ Shows logs URL """

    phenny.say("Logs at %s" % endpoints['log'])

logs.commands = ['logs', 'log']
logs.priority = 'low'
logs.example = '.logs'
