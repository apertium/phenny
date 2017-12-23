#!/usr/bin/env python
# coding=utf-8
"""
calc.py - Phenny Calculator Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web

subs = [
    ('£', 'GBP '),
    ('€', 'EUR '),
    ('\$', 'USD '),
    (r'\n', '; '),
    ('&deg;', '°'),
    (r'\/', '/'),
]


def c(phenny, input):
    """DuckDuckGo calculator."""

    # This module is going to be rewritten
    self.skipTest(self.skip_msg.format('Bing'))

    if not input.group(2):
        return phenny.reply("Nothing to calculate.")
    q = input.group(2)

    try:
        r = web.get(
            'https://api.duckduckgo.com/?q={}&format=json&no_html=1'
            '&t=mutantmonkey/phenny'.format(web.quote(q)))
    except web.HTTPError:
        raise GrumbleError("Couldn't parse the result from DuckDuckGo.")

    data = web.json(r)
    if data['AnswerType'] == 'calc':
        answer = data['Answer'].split('=')[-1].strip()
    else:
        answer = None

    if answer:
        phenny.say(answer)
    else:
        phenny.reply('Sorry, no result.')
c.commands = ['c']
c.example = '.c 5 + 3'

def py(phenny, input): 
   """evaluates a python2 expression via a remote sandbox"""
   query = input.group(2).encode('utf-8')
   uri = 'http://tumbolia.appspot.com/py/'
   answer = web.get(uri + web.quote(query))
   if answer: 
      phenny.say(answer)
   else: phenny.reply('Sorry, no result.')
py.commands = ['py']
py.example = '.py if not False: print "hello world!"'

def wa(phenny, input): 
    """Query Wolfram Alpha."""
    
    if not input.group(2):
        return phenny.reply("No search term.")
    query = input.group(2)

    re_output = re.compile(r'{"stringified": "(.*?)",')

    uri = 'http://www.wolframalpha.com/input/?i={}'
    out = web.get(uri.format(web.quote(query)))
    answers = re_output.findall(out)
    if len(answers) <= 0:
        phenny.reply("Sorry, no result.")
        return

    answer = answers[1]
    for sub in subs:
        answer = answer.replace(sub[0], sub[1])

    phenny.say(answer)
wa.commands = ['wa']
wa.example = '.wa answer to life'

if __name__ == '__main__':
    print(__doc__.strip())
