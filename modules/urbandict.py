#!/usr/bin/python3
"""
urbandict.py - urban dictionary module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import GrumbleError
import web
import json
import re
from bot import command

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

@command('urb', example='.urb troll')
def urbandict(phenny, msg):
    """.urb <word> - Search Urban Dictionary for a definition. (supports pointing)"""

    word = msg.command_args
    if not word:
        phenny.say(urbandict.__doc__.strip())
        return
    to_nick = msg.command_point

    get_definition(phenny, word, to_user=to_nick)

if __name__ == '__main__':
    print(__doc__.strip())
