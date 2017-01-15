#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web

from googleapiclient.discovery import build

my_api_key = "AIzaSyDiWn9tB9NzxIxkohXXN6GNBNPRep6hIWM"
my_cse_id = "017800230218291994756:re9_m1koe44"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def gsearch(phenny, input):
    str = input.replace(".g ", "")
    results = google_search(
        str, my_api_key, my_cse_id, num=10)
    for result in results[:1]:
        phenny.say("{} : {}".format(result['title'], result['link']))

gsearch.commands = ['g']
gsearch.name = 'g'
gsearch.example = '.g Apertium'

r_bing = re.compile(r'<h2><a href="([^"]+)"')

def bing_search(query, lang='en-GB'): 
    query = web.quote(query)
    base = 'https://www.bing.com/search?mkt=%s&q=' % lang
    bytes = web.get(base + query)
    m = r_bing.search(bytes)
    if m: return m.group(1)

def bing(phenny, input): 
    """Queries Bing for the specified input."""
    query = input.group(2)
    if query.startswith(':'): 
        lang, query = query.split(' ', 1)
        lang = lang[1:]
    else: lang = 'en-GB'
    if not query:
        return phenny.reply('.bing what?')

    uri = bing_search(query, lang)
    if uri: 
        phenny.reply(uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.reply("No results found for '%s'." % query)
bing.commands = ['bing']
bing.example = '.bing swhack'

r_duck = re.compile(r'nofollow" class="[^"]+" href=".*(http.*?)">')

def duck_search(query): 
    query = query.replace('!', '')
    query = web.quote(query)
    uri = 'https://duckduckgo.com/html/?q=%s&kl=uk-en' % query
    bytes = web.get(uri)
    m = r_duck.search(bytes)
    if m: return web.decode(m.group(1))

def duck(phenny, input): 
    """Queries DuckDuckGo for specified input."""
    query = input.group(2)
    if not query: return phenny.reply('.ddg what?')

    uri = duck_search(query)
    if uri: 
        phenny.reply(uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.reply("No results found for '%s'." % query)
duck.commands = ['duck', 'ddg']
duck.example = '.duck football'

def search(phenny, input): 
    if not input.group(2): 
        return phenny.reply('.search for what?')
    query = input.group(2)
    gu = google_search(query) or '-'
    bu = bing_search(query) or '-'
    du = duck_search(query) or '-'

    if (gu == bu) and (bu == du): 
        result = '%s (g, b, d)' % gu
    elif (gu == bu): 
        result = '%s (g, b), %s (d)' % (gu, du)
    elif (bu == du): 
        result = '%s (b, d), %s (g)' % (bu, gu)
    elif (gu == du): 
        result = '%s (g, d), %s (b)' % (gu, bu)
    else: 
        if len(gu) > 250: gu = '(extremely long link)'
        if len(bu) > 150: bu = '(extremely long link)'
        if len(du) > 150: du = '(extremely long link)'
        result = '%s (g), %s (b), %s (d)' % (gu, bu, du)

    phenny.reply(result)
search.commands = ['search']

def suggest(phenny, input): 
    if not input.group(2):
        return phenny.reply("No query term.")
    query = input.group(2)
    uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
    answer = web.get(uri + web.quote(query).replace('+', '%2B'))
    if answer: 
        phenny.say(answer)
    else: phenny.reply('Sorry, no result.')
suggest.commands = ['suggest']

def lmgtfy(phenny, input):
    if not input.group(2):
        phenny.reply('.lmgtfy what f who?')
    try:
        (who, what) = input.group(2).split(' ', 1)
        response = "%s: http://lmgtfy.com/?q=%s"
        what = web.quote(what)
        phenny.say(response % (who, what))
    except ValueError:
        phenny.reply('.lmgtfy what for who? (enter a nick and a query)')
lmgtfy.commands = ['lmgtfy']

if __name__ == '__main__': 
    print(__doc__.strip())
