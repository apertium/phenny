#!/usr/bin/env python
"""
vtluugwiki.py - Phenny VTLUUG Wiki Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

modified from Wikipedia module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import truncate
import wiki

wikiapi = 'https://vtluug.org/w/api.php?action=query&list=search&srsearch={0}&limit=1&prop=snippet&format=json'
wikiuri = 'https://vtluug.org/wiki/{0}'
wikisearch = 'https://vtluug.org/wiki/Special:Search?' \
                          + 'search={0}&fulltext=Search'

def vtluug(phenny, input): 
    """.vtluug <term> - Look up something on the VTLUUG wiki."""

    origterm = input.group(1)

    if not origterm:
        return phenny.say('Perhaps you meant ".vtluug VT-Wireless"?')

    term, section = wiki.parse_term(origterm)

    w = wiki.Wiki(wikiapi, wikiuri, wikisearch)
    url = w.search(term)

    if not url:
        phenny.say('Can\'t find anything in the VTLUUG Wiki for "{0}".'.format(term))
        return

    snippet, url = wiki.extract_snippet(url, section)

    phenny.say(truncate(snippet, '"%s" - ' + url))

vtluug.commands = ['vtluug']
vtluug.priority = 'high'

if __name__ == '__main__': 
    print(__doc__.strip())
