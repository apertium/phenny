#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web
import json
import requests
from tools import is_up

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

def duck_search(q):
    if not is_up('https://api.duckduckgo.com'):
        return 'Sorry, DuckDuckGo API is down.'

    uri = 'https://api.duckduckgo.com/?format=json&pretty=1&q='
    r = requests.get(uri + q)
    try:
        answer = r.json()['AbstractText']
        if answer == '':
            answer = r.json()['RelatedTopics'][0]['Text'] + ' ' + r.json()['RelatedTopics'][0]['FirstURL']
            if answer == '':
                return 'Sorry, no result.'
    except:
        return 'Sorry, no result.'
    return answer

def topics(phenny, input):
    if not is_up('https://api.duckduckgo.com'):
        return phenny.say('Sorry, DuckDuckGo API is down.')

    if not input.group(2): 
        return phenny.reply('.topics about what?')
    query = input.group(2)

    uri = 'https://api.duckduckgo.com/?format=json&pretty=1&q='
    r = requests.get(uri + query)
    try:
        topics = r.json()['RelatedTopics']
        if len(topics) == 0:
            return phenny.say('Sorry, no topics found.')
        counter = 0
        for topic in r.json()['RelatedTopics']:
            if counter < 3:
                phenny.say(topic['Text'] + ' - ' + topic['FirstURL'])
            else:
                break
            counter += 1
        if len(topics) < 3:
            phenny.reply('No more topics found.')
    except:
        return phenny.say('Sorry, no more topics found.')
topics.commands = ['topics']

def search(phenny, input):
    if not input.group(2): 
        return phenny.reply('.search for what?')
    query = input.group(2)
    answer = duck_search(query)
    phenny.say(answer)
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
