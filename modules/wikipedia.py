#!/usr/bin/env python
"""
wikipedia.py - Phenny Wikipedia Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re

from tools import truncate
import wiki

endpoints = {
    'api': 'https://%s.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch={0}&prop=snippet&limit=1',
    'url': 'https://%s.wikipedia.org/wiki/{0}',
    'search': 'https://%s.wikipedia.org/wiki/Special:Search?search={0}&fulltext=Search',
}

langs = ['ar', 'bg', 'ca', 'cs', 'da', 'de', 'en', 'es', 'eo', 'eu', 'fa', 'fr', 'ko', 'hi', 'hr', 'id', 'it', 'he', 'lt', 'hu', 'ms', 'nl', 'ja', 'no', 'pl', 'pt', 'kk', 'ro', 'ru', 'sk', 'sl', 'sr', 'fi', 'sv', 'tr', 'uk', 'vi', 'vo', 'war', 'zh']


def wikipedia(phenny, origterm, lang, to_user=None):
    if not origterm:
        return phenny.say('Perhaps you meant ".wik Zen"?')

    origterm = origterm.strip()
    lang = lang.strip()

    term, section = wiki.parse_term(origterm)

    w = wiki.Wiki(endpoints, lang)
    match = w.search(term)

    if not match:
        phenny.say('Can\'t find anything in Wikipedia for "{0}".'.format(origterm))
        return

    snippet, url = wiki.extract_snippet(match, section)

    if to_user:
        phenny.say(truncate(snippet, to_user + ', "{}" - ' + url))
    else:
        phenny.say(truncate(snippet, '"{}" - ' + url))


def wik(phenny, input):
    """Search for something on Wikipedia (supports pointing)"""

    origterm = input.group(3)
    if input.group(2):
        lang = input.group(2)[1:]
    else:
        lang = "en"

    to_nick = input.group(4)

    wikipedia(phenny, origterm, lang, to_user=to_nick)

wik.rule = r'\.(wik|wiki|wikipedia)(\.[a-z]{2,3})?\s(.*)'
wik.priority = 'low'
wik.example = '.wik Human'
wik.point = True


def wik2(phenny, input):
    nick, _, __, lang, origterm = input.groups()
    if not lang: lang = "en"

    wikipedia(phenny, origterm, lang, to_user=nick)

wik2.rule = r'(\S*)(:|,)\s\.(wik|wiki|wikipedia)(\.[a-z]{2,3})?\s(.*)'
wik2.priority = 'high'
wik2.example = 'svineet: .wik Linguistics'


def pointing(phenny, input):
    """ Begiak also supports pointing users to the output of other commands.
    For example, .wik India -> nick will make Begiak say:
    nick, "India, officially the Republic of India (Bhārat Gaṇarājya),
    [18][19][c] is a country in South Asia" - https://en.wikipedia.org/wiki/India
    . Do .awik Begiak for more information on supported commands.
    """
    pass

pointing.commands = ['pointing']


if __name__ == '__main__':
    print(__doc__.strip())
