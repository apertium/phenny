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
from tools import is_up, truncate
from modules import more

ddg_uri = 'https://api.duckduckgo.com/?format=json&pretty=1&q='  

def topics(phenny, input):
    if not is_up('https://api.duckduckgo.com'):
        return phenny.say('Sorry, DuckDuckGo API is down.')

    if not input.group(2): 
        return phenny.reply('.topics about what?')
    query = input.group(2)

    r = requests.get(ddg_uri + query).json()
    topics = r['RelatedTopics']
    if len(topics) == 0:
        return phenny.say('Sorry, no topics found.')
    topics_list = []
    counter = 0
    for topic in r['RelatedTopics']:
        if counter < 10:
            try:
                topics_list.append(topic['Text'] + ' - ' + topic['FirstURL'])
            except:
                continue
        else:
            break
    more.add_messages(input.nick, phenny, topics_list)
topics.commands = ['topics']

def search(phenny, input):
    if not input.group(2): 
        return phenny.reply('.search for what?')
    query = input.group(2)

    if not is_up('https://api.duckduckgo.com'):
        return phenny.say('Sorry, DuckDuckGo API is down.')

    r = requests.get(ddg_uri + query).json()
    try:
        answer = r['AbstractText']
        answer_url = r['AbstractURL']
        if answer == '':
            answer = r['RelatedTopics'][0]['Text']
            answer_url = r['RelatedTopics'][0]['FirstURL']
            if answer == '':
                return phenny.say('Sorry, no result.')
    except:
        return phenny.say('Sorry, no result.')
    phenny.say(truncate(answer, share=' - ' + r['AbstractURL']) + ' - ' + answer_url)
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
