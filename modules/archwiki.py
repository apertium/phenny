#!/usr/bin/env python
"""
archwiki.py - Phenny ArchWiki Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

modified from Wikipedia module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import truncate
import wiki

wikiapi = 'https://wiki.archlinux.org/api.php?action=query&list=search&srsearch={0}&limit=1&format=json'
wikiuri = 'https://wiki.archlinux.org/index.php/{0}'
wikisearch = 'https://wiki.archlinux.org/index.php/Special:Search?' \
                          + 'search={0}&fulltext=Search'

def awik(phenny, input): 
    origterm = input.group(1)

    if not origterm:
        return phenny.say('Perhaps you meant ".awik dwm"?')

    term, section = wiki.parse_term(origterm)

    w = wiki.Wiki(wikiapi, wikiuri, wikisearch)
    url = w.search(term)

    if not url:
        phenny.say('Can\'t find anything in the ArchWiki for "{0}".'.format(term))
        return

    snippet, url = wiki.extract_snippet(url, section)

    phenny.say(truncate(snippet, '"%s" - ' + url))

awik.commands = ['awik']
awik.priority = 'high'

if __name__ == '__main__': 
    print(__doc__.strip())
