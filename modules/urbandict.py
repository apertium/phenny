#!/usr/bin/python3
"""
urbandict.py - urban dictionary module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import GrumbleError
import web
import json
import re


def get_definition(phenny, word, to_user=None):
    try:
        data = web.get(
            "http://api.urbandictionary.com/v0/define?term={0}".format(
                web.quote(word)))
        data = json.loads(data)
    except:
        raise GrumbleError(
            "Urban Dictionary slemped out on me. Try again in a minute.")

    if data['result_type'] == 'no_results':
        phenny.say("No results found for {0}".format(word))
        return

    result = data['list'][0]
    url = 'http://www.urbandictionary.com/define.php?term={0}'.format(
        web.quote(word))

    response = "{0} - {1}".format(result['definition'].strip()[:256], url)
    if to_user:
        phenny.say(to_user+', '+response)
    else:
        phenny.say(response)


def urbandict(phenny, input):
    """.urb <word> - Search Urban Dictionary for a definition."""

    word = input.group(2)
    if not word:
        phenny.say(urbandict.__doc__.strip())
        return

    if "->" in word: return
    if "→" in word: return

    # create opener
    #opener = urllib.request.build_opener()
    #opener.addheaders = [
    #    ('User-agent', web.Grab().version),
    #    ('Referer', "http://m.urbandictionary.com"),
    #]

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(word)
    if matched_point:
        to_nick = matched_point.groups()[0]
        word2 = matched_point.groups()[1]
        
        get_definition(phenny, word2, to_user=to_nick)
        return

    get_definition(phenny, word)

    
urbandict.name = 'urb'
urbandict.rule = (['urb'], r'(.*)')
urbandict.example = '.urb troll or nick: .urb troll or .urb troll -> nick'+\
                    ' or .urb point nick troll'


def urbandict2(phenny, input):
    _, word, __, nick = input.groups()

    get_definition(phenny, word, to_user=nick)


urbandict2.rule = r'\.(urb)\s(.*)\s(->|→)\s(\S*)'
urbandict2.example = '.urb seppuku -> svineet'


def urbandict3(phenny, input):
    nick, _, __, word = input.groups()

    get_definition(phenny, word, nick)

urbandict3.rule = r'(\S*)(:|,)\s\.(urb)\s(.*)'
urbandict3.example = 'svineet: .urb seppuku'


if __name__ == '__main__':
    print(__doc__.strip())
