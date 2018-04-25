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

    if "->" in origterm or "→" in origterm:
        return

    if not origterm:
        return phenny.say('Perhaps you meant ".wik Zen"?')

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(origterm)
    to_nick = None
    if matched_point:
        to_nick = matched_point.groups()[0]
        origterm = matched_point.groups()[1]

    apertium_wiki(phenny, origterm, to_nick=to_nick)


awik.rule = r'\.(awik)\s(.*)'
awik.example = '.awik Begiak or .awik point nick Begiak or .awik Begiak -> nick' ' or nick: .awik Begiak'
awik.priority = 'high'


def awik2(phenny, input):
    nick, _, __, lang, origterm = input.groups()
    apertium_wiki(phenny, origterm, nick)


awik2.rule = r'(\S*)(:|,)\s\.(awik)(\.[a-z]{2,3})?\s(.*)'
awik2.example = 'svineet: .awik Begiak'
awik2.priority = 'high'


def awik3(phenny, input):
    _, lang, origterm, nick = input.groups()
    apertium_wiki(phenny, origterm, nick)


awik3.rule = r'\.(awik)(\.[a-z]{2,3})?\s(.*)'
awik3.example = '.awik Linguistics -> svineet'
awik3.point = True


def logs(phenny, input):
    """ Shows logs URL """

    phenny.say("Logs at %s" % endpoints['log'])

logs.commands = ['logs', 'log']
logs.priority = 'low'
logs.example = '.logs'
