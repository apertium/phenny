#!/usr/bin/python3
"""
randomquote.py - urban dictionary module
author: jonorthwash <jonorthwash@users.sourceforge.net>
"""

from tools import GrumbleError
import web
import json
from requests import HTTPError

from bot import command

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
    url = "http://quotes.firespeaker.org/random.php"
    if topic:
        url += "?topic=%s" % web.quote(topic)
    try:
        data = web.api_call(url, headers=[
            ('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17'),
            ('Referer', "http://quotes.firespeaker.org/"),
        ])
    except (HTTPError, IOError, ValueError) as e:
        raise GrumbleError("Firespeaker.org down? Try again later.") from e

    if len(data) == 0:
        phenny.say("No results found")
        return

    if data['quote'] != None:
        quote = data['quote'].replace('</p>', '').replace('<p>', '').replace('<em>', '_').replace('</em>', '_').replace('&mdash;', '—')
        response = data['short_url'] + ' - ' + quote
    else:
        phenny.say("Sorry, no quotes returned!")
        return

    msg = response.splitlines()
    if msg:
        phenny.say(msg[0], target=to_user)

@command('randquote', priority='low', example='.randquote linguistics')
def randquote(phenny, msg):
    """.randquote (<topic>) - Get a random quote from quotes.firespeaker.org (about topic). (supports pointing)"""
    randquote_fetcher(phenny, msg.command_args, msg.command_point or msg.nick)

if __name__ == '__main__':
    print(__doc__.strip())
