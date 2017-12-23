#!/usr/bin/env python
"""
imdb.py - Phenny Web Search Module
Copyright 2012, Randy Nance, randynance.info 
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import json
import web

# SHOULD BE API KEY INCLUDED HERE '?apikey={apikey}'
uri_template = 'http://www.omdbapi.com/?i=&t=%s'

def imdb_search(query): 
    query = query.replace('!', '')
    query = query.encode('utf-8')
    query = web.quote(query)
    uri = uri_template % query
    bytes = web.get(uri)
    m = json.loads(bytes)
    return m


def imdb(phenny, input): 
    """.imdb <movie> - Use the OMDB API to find a link to a movie on IMDb."""

    query = input.group(2)
    if not query:
        return phenny.say('.imdb what?')

    m = imdb_search(query)
    try:
        phenny.say('{0} ({1}): {2}  http://imdb.com/title/{3}'.format(
            m['Title'],
            m['Year'],
            m['Plot'],
            m['imdbID']))
    except:
        phenny.reply("No results found for '%s'." % query)
imdb.example = '.imdb Prometheus'
imdb.commands = ['imdb']
imdb.example = '.imdb Promethius'
