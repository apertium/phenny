#!/usr/bin/python3
"""
randomquote.py - urban dictionary module
author: jonorthwash <jonorthwash@users.sourceforge.net>
"""

import urllib.request
from urllib.error import HTTPError
from tools import GrumbleError
import web
import json
from modules import more

from bot import command

#FIXME: need to implement
#def quote(phenny, input):
#    """.quote <id> - Get a quote from quotes.firespeaker.org."""
#
#    word = input.group(1)
#    if not word:
#        phenny.say(fs_quotes.__doc__.strip())
#        return
#    # create opener
#    opener = urllib.request.build_opener()
#    opener.addheaders = [
#        ('User-agent', web.Grab().version),
#        ('Referer', "http://quotes.firespeaker.org"),
#    ]
#
#    try:
#        req = opener.open("http://api.urbandictionary.com/v0/define?term={0}"
#                .format(web.quote(word)))
#        data = req.read().decode('utf-8')
#        data = json.loads(data)
#    except (HTTPError, IOError, ValueError) as e:
#        raise GrumbleError(
#                "Urban Dictionary slemped out on me. Try again in a minute.") from e
#
#    if data['result_type'] == 'no_results':
#        phenny.say("No results found for {0}".format(word))
#        return
#
#    result = data['list'][0]
#    url = 'http://www.urbandictionary.com/define.php?term={0}'.format(web.quote(word))
#
#    response = "{0} - {1}".format(result['definition'].strip()[:256], url)
#    phenny.say(response)

topics = {"particles": "\"particle\" stands for \"defeat\" -spectie",
    "installing apertium": "try \"installing apertium on <operating system>\"",
    "installing apertium on ubuntu": "https://wiki.apertium.org/wiki/Apertium_on_Ubuntu",
    "installing apertium on linux": "https://wiki.apertium.org/wiki/Apertium_on_Ubuntu",
    "installing apertium on windows": "https://wiki.apertium.org/wiki/Apertium_on_Windows",
    "google summer of code": "https://wiki.apertium.org/wiki/Google_Summer_of_Code",
    "gsoc": "https://wiki.apertium.org/wiki/Google_Summer_of_Code",
    "spectie": "https://wiki.apertium.org/wiki/User:Francis_Tyers",
    "firespeaker": "https://wiki.apertium.org/wiki/User:Firespeaker",
    "zfe": "http://quotes.firespeaker.org/?who=zfe"
    }

@command('information', example='.information installing apertium', priority='low')
def information(phenny, msg):
    """.information (<topic>) get information on a topic"""
    topic = msg.command_args.lower()
    if topic in topics:
        phenny.say(topics[topic])
    else:
        phenny.say("Sorry, no information on %s is currently available ☹" % topic)


def randquote_fetcher(phenny, topic, to_user):
    # create opener
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-agent', web.Grab().version),
        ('Referer', "http://quotes.firespeaker.org/"),
    ]

    try:
        url = "http://quotes.firespeaker.org/random.php"
        if topic:
            url += "?topic=%s" % web.quote(topic)
        req = opener.open(url)
        data = req.read().decode('utf-8')
        data = json.loads(data)
    except (HTTPError, IOError, ValueError) as e:
        raise GrumbleError("Firespeaker.org down? Try again later.") from e

    if len(data) == 0:
        phenny.say("No results found")
        return

    #result = data['list'][0]
    #url = 'http://www.urbandictionary.com/define.php?term={0}'.format(web.quote(word))
    #
    #response = "{0} - {1}".format(result['definition'].strip()[:256], url)

    if data['quote'] != None:
        quote = data['quote'].replace('</p>', '').replace('<p>', '').replace('<em>', '_').replace('</em>', '_').replace('&mdash;', '—')
        response = data['short_url'] + ' - ' + quote
    else:
        phenny.say("Sorry, no quotes returned!")
        return

    more.add_messages(phenny, to_user, response.split('\n'))

@command('randquote', priority='low', example='.randquote linguistics')
def randquote(phenny, msg):
    """.randquote (<topic>) - Get a random quote from quotes.firespeaker.org (about topic). (supports pointing)"""
    randquote_fetcher(phenny, msg.command_args, msg.command_point or msg.nick)

if __name__ == '__main__':
    print(__doc__.strip())
