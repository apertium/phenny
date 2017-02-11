#!/usr/bin/env python
"""
imdb.py - Phenny Web Search Module
Copyright 2012, Randy Nance, randynance.info 
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web

r_imdb_find = re.compile(r'href="/title/(.*?)/')
r_imdb_details = re.compile(r'<title>(.*?) \((.*?)\) .*?name="description" content="(.*?)"')

def imdb_search(query):
    query = query.replace('!', '')
    query = web.quote(query)
    uri = 'http://imdb.com/find?q=%s' % query
    bytes = web.get(uri)
    m = r_imdb_find.search(bytes)
    if not m: return m
    ID = web.decode(m.group(1))
    uri = 'http://imdb.com/title/%s' % ID
    bytes = web.get(uri)
    bytes = bytes.replace('\n', '')
    info = r_imdb_details.search(bytes)
    info = {'Title': info.group(1), 'Year': info.group(2), 'Plot': info.group(3), 'imdbID': ID}
    return info


def imdb(phenny, input): 
    """.imdb <movie> - Find a link to a movie on IMDb."""

    query = input.group(2)
    if not query:
        return phenny.say('.imdb what?')

    m = imdb_search(query)
    if m:
        phenny.say('{0} ({1}): {2}  http://imdb.com/title/{3}'.format(
            m['Title'],
            m['Year'],
            m['Plot'],
            m['imdbID']))
    else:
        phenny.reply("No results found for '%s'." % query)
imdb.example = '.imdb Prometheus'
imdb.commands = ['imdb']
imdb.example = '.imdb Promethius'
