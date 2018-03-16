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

wikiapi = 'https://%s.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch={0}&prop=snippet&limit=1'
wikiuri = 'https://%s.wikipedia.org/wiki/{0}'
wikisearch = 'https://%s.wikipedia.org/wiki/Special:Search?search={0}&fulltext=Search'

langs = ['ar', 'bg', 'ca', 'cs', 'da', 'de', 'en', 'es', 'eo', 'eu', 'fa', 'fr', 'ko', 'hi', 'hr', 'id', 'it', 'he', 'lt', 'hu', 'ms', 'nl', 'ja', 'no', 'pl', 'pt', 'kk', 'ro', 'ru', 'sk', 'sl', 'sr', 'fi', 'sv', 'tr', 'uk', 'vi', 'vo', 'war', 'zh']


def wikipedia(phenny, origterm, lang, to_user=None):
    if not origterm:
        return phenny.say('Perhaps you meant ".wik Zen"?')

    origterm = origterm.strip()
    lang = lang.strip()

    term, section = wiki.parse_term(origterm)

    w = wiki.Wiki(wikiapi % lang, wikiuri % lang, wikisearch % lang)
    url = w.search(term)

    if not url:
        phenny.say('Can\'t find anything in Wikipedia for "{0}".'.format(origterm))
        return

    snippet, url = wiki.extract_snippet(url, section)

    if to_user:
        phenny.say(truncate(snippet, to_user + ', "%s" - ' + url))
    else:
        phenny.say(truncate(snippet, '"%s" - ' + url))


def wik(phenny, input):
    """Search for something on Wikipedia (supports pointing)"""
    if "->" in input.group(3): return
    if "→" in input.group(3): return

    origterm = input.group(3)
    if input.group(2):
        lang = input.group(2)[1:]
    else:
        lang = "en"

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(origterm)
    if matched_point:
        to_nick = matched_point.groups()[0]
        origterm2 = matched_point.groups()[1]

        wikipedia(phenny, origterm2, lang, to_user=to_nick)
        return

    wikipedia(phenny, origterm, lang)

wik.rule = r'\.(wik|wiki|wikipedia)(\.[a-z]{2,3})?\s(.*)'
wik.priority = 'low'
wik.example = '.wik Human or nick: .wik Human or .wik Human -> nick'+\
            ' or .wik point nick Human'


def wik2(phenny, input):
    nick, _, __, lang, origterm = input.groups()
    if not lang: lang = "en"

    wikipedia(phenny, origterm, lang, to_user=nick)

wik2.rule = r'(\S*)(:|,)\s\.(wik|wiki|wikipedia)(\.[a-z]{2,3})?\s(.*)'
wik2.priority = 'high'
wik2.example = 'svineet: .wik Linguistics'


def wik3(phenny, input):
    _, lang, origterm, __, nick = input.groups()
    if not lang: lang = "en"

    wikipedia(phenny, origterm, lang, to_user=nick)

wik3.rule = r'\.(wik|wiki|wikipedia)(\.[a-z]{2,3})?\s(.*)\s(->|→)\s(\S*)'
wik3.priority = 'high'
wik3.example = '.wik Linguistics -> svineet'


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
