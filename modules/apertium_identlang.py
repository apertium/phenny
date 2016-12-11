#!/usr/bin/env python
# coding=utf-8
"""
apertium_identlang.py
"""

import re
import urllib.request
import json
import web
from tools import GrumbleError, translate
from modules import more

headers = [(
    'User-Agent', 'Mozilla/5.0' +
    '(X11; U; Linux i686)' +
    'Gecko/20071127 Firefox/2.0.0.11'
)]

APIurl = "http://apy.projectjj.com"

APIerrorData = 'Sorry, the apertium API did not return any data '
APIerrorHttp = 'Sorry, the apertium API gave HTTP error %s: %s '


def apertium_identlang(phenny, input):
    """Identify Language using Apertium APY"""
    lang, text = input.groups()

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = APIurl + '/identifyLang?q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
        jdata = json.loads(response.decode('utf-8'))
    except urllib.error.HTTPError as error:
        response = error.read()
        phenny.say(response)
    messages = []
    for key, value in jdata.items():
        messages.append(key + " = " + str(value))
    more.add_messages(input.nick, phenny,
                      "\n".join(messages),
                      break_up=lambda x, y: x.split('\n'))

apertium_identlang.name = 'identlang'
apertium_identlang.commands = ['identlang']
apertium_identlang.example = '.identlang Whereas disregard and contempt for which have outraged the conscience of mankind'
apertium_identlang.priority = 'high'
