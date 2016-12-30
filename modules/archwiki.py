#!/usr/bin/env python
"""
archwiki.py - Phenny ArchWiki Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

modified from Wikipedia module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import re
import web
import wiki

wikiapi = 'https://wiki.archlinux.org/api.php?action=query&list=search&srsearch={0}&limit=1&format=json'
wikiuri = 'https://wiki.archlinux.org/index.php/{0}'
wikisearch = 'https://wiki.archlinux.org/index.php/Special:Search?' \
                          + 'search={0}&fulltext=Search'

def awik(phenny, input): 
    origterm = input.groups()[1]
    if not origterm: 
        return phenny.say('Perhaps you meant ".awik dwm"?')

    term = web.unquote(origterm)
    term = term[0].upper() + term[1:]
    term = term.replace(' ', '_')

    w = wiki.Wiki(wikiapi, wikiuri, wikisearch)

    try:
        result = w.search(term)
    except web.ConnectionError:
        error = "Can't connect to wiki.archlinux.org ({0})".format(wikiuri.format(term))
        return phenny.say(error)

    if result is not None: 
        phenny.say(result)
    else:
        phenny.say('Can\'t find anything in the ArchWiki for "{0}".'.format(origterm))

awik.commands = ['awik']
awik.priority = 'high'

if __name__ == '__main__': 
    print(__doc__.strip())
