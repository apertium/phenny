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
from bot import command

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


@command(['wik', 'wiki', 'wikipedia'], example='.wik Human')
def wik(phenny, msg):
    """Search for something on Wikipedia (supports pointing)"""

    wikipedia(phenny, msg.command_args, msg.sub_command or 'en',
              to_user=msg.command_point)

@command('pointing')
def pointing(phenny, msg):
    """ Begiak also supports pointing users to the output of other commands.
    For example, .wik India -> nick will make Begiak say:
    nick, "India, officially the Republic of India (Bhārat Gaṇarājya),
    [18][19][c] is a country in South Asia" - https://en.wikipedia.org/wiki/India
    . Do .awik Begiak for more information on supported commands.
    """
    pass

if __name__ == '__main__':
    print(__doc__.strip())
