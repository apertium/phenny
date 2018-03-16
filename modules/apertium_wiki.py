#!/usr/bin/env python
"""
apertium_wiki.py - Phenny Wikipedia Module
"""

import re
import json
from urllib.parse import quote

from tools import truncate
import web
import wiki

wikiuri = 'http://wiki.apertium.org/wiki/{:s}'
wikisearchuri = 'http://wiki.apertium.org/api.php?action=query&list=search&srlimit=1&format=json&srsearch={:s}&srwhat={:s}'
LOGS_URL = "http://tinodidriksen.com/pisg/freenode/logs/"


def apertium_wiki(phenny, origterm, to_nick=None):
    term = wiki.format_term(origterm)
    term = quote(term)

    try:
        url = wikiuri.format(term)
        web.get(url)
    except:
        for srwhat in ['title', 'text']:
            response = json.loads(web.get(wikisearchuri.format(term, srwhat)))

            if len(response['query']['search']):
                term = response['query']['search'][0]['title']
                term = wiki.format_term(term)
                term = quote(term)
                url = wikiuri.format(term)
                break
        else:
            phenny.reply("No wiki results for that term.")
            return

    snippet, url = wiki.extract_snippet(url, None)

    if to_nick:
        phenny.say(truncate(snippet, to_nick + ', "%s" - ' + url))
    else:
        phenny.say(truncate(snippet, '"%s" - ' + url))


def awik(phenny, input):
    """Search for something on Apertium wiki or
    point another user to a page on Apertium wiki (supports pointing)"""
    origterm = input.groups()[1]

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
    _, lang, origterm, __, nick = input.groups()
    apertium_wiki(phenny, origterm, nick)


awik3.rule = r'\.(awik)(\.[a-z]{2,3})?\s(.*)\s(->|→)\s(\S*)'
awik3.example = '.awik Linguistics -> svineet'


def logs(phenny, input):
    """ Shows logs URL """

    phenny.say("Logs at %s" % LOGS_URL)

logs.commands = ['logs', 'log']
logs.priority = 'low'
logs.example = '.logs'
