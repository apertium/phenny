#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web
from tools import truncate
from modules import more
import web
from bot import command

ddg_uri = 'https://api.duckduckgo.com/?format=json&pretty=1&q='
suggest_uri = 'http://suggestqueries.google.com/complete/search?client=firefox&hl=en&q='

@command('g')
def gsearch(phenny, msg):
    phenny.reply('.g is deprecated. Try .search powered by Duck Duck Go instead.')

@command('topics')
def topics(phenny, msg):
    if not web.is_up('https://api.duckduckgo.com'):
        return phenny.say('Sorry, DuckDuckGo API is down.')

    if not msg.command_args:
        return phenny.reply('.topics about what?')
    query = msg.command_args

    r = web.api_call(ddg_uri + query)
    topics = r['RelatedTopics']
    if len(topics) == 0:
        return phenny.say('Sorry, no topics found.')
    topics_list = []
    counter = 0
    for topic in r['RelatedTopics'][:10]:
        try:
            topics_list.append(topic['Text'] + ' - ' + topic['FirstURL'])
        except KeyError:
            continue
    phenny.say(topics_list[0])
    phenny.reply('Check PM for more topics.')
    more.add_messages(phenny, msg.nick, topics_list[1:])

@command('search')
def search(phenny, msg):
    if not msg.command_args:
        return phenny.reply('.search for what?')
    query = msg.command_args

    if not web.is_up('https://api.duckduckgo.com'):
        return phenny.say('Sorry, DuckDuckGo API is down.')

    r = web.api_call(ddg_uri + query)
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
    # Removes html tags, if exist
    answer = re.sub('<.+?>', '', answer)
    phenny.say(truncate(answer, '{} - ' + answer_url))

@command('suggest')
def suggest(phenny, msg):
    ''' Shows first 10 results from Google Suggestion API.'''
    if not msg.command_args:
        return phenny.reply("No query term.")
    query = msg.command_args
    answer = web.api_call(suggest_uri + query)
    suggestions = answer[1][:10]
    phenny.reply(suggestions[0])
    phenny.reply('Check PM for more.')
    more.add_messages(phenny, msg.nick, suggestions[1:])

@command('lmgtfy')
def lmgtfy(phenny, msg):
    if not msg.command_args:
        phenny.reply('.lmgtfy what f who?')
    try:
        (who, what) = msg.command_args.split(' ', 1)
        response = "%s: http://lmgtfy.com/?q=%s"
        what = web.quote(what)
        phenny.say(response % (who, what))
    except ValueError:
        phenny.reply('.lmgtfy what for who? (enter a nick and a query)')

if __name__ == '__main__':
    print(__doc__.strip())
