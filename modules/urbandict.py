#!/usr/bin/python3
"""
urbandict.py - urban dictionary module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import GrumbleError
import web
import json
import re


API_URL = "http://api.urbandictionary.com/v0/define?term={0}"
WEB_URL = "http://www.urbandictionary.com/define.php?term={0}"

def get_definition(phenny, word, to_user=None):
    data = web.get(API_URL.format(web.quote(word)))
    data = json.loads(data)

    results = data['list']

    if not results:
        phenny.say("No results found for {0}".format(word))
        return

    result = results[0]
    url = WEB_URL.format(web.quote(word))

    response = "{0} - {1}".format(result['definition'].strip()[:256], url)
    phenny.say(response, target=to_user)


def urbandict(phenny, input):
    """.urb <word> - Search Urban Dictionary for a definition. (supports pointing)"""

    word = input.group(1)
    if not word:
        phenny.say(urbandict.__doc__.strip())
        return
    to_nick = input.group(2)

    get_definition(phenny, word, to_user=to_nick)


urbandict.name = 'urb'
urbandict.rule = (['urb'], r'(.*)')
urbandict.example = '.urb troll'
urbandict.point = True


def urbandict3(phenny, input):
    nick, _, __, word = input.groups()

    get_definition(phenny, word, nick)

urbandict3.rule = r'(\S*)(:|,)\s\.(urb)\s(.*)'
urbandict3.example = 'svineet: .urb seppuku'


if __name__ == '__main__':
    print(__doc__.strip())
