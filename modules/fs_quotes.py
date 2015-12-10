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

#FIXME: need to implement
#def quote(phenny, input):
#    """.quote <id> - Get a quote from quotes.firespeaker.org."""
#
#    word = input.group(2)
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
#    except (HTTPError, IOError, ValueError):
#        raise GrumbleError(
#                "Urban Dictionary slemped out on me. Try again in a minute.")
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
	"installing apertium on ubuntu": "http://wiki.apertium.org/wiki/Apertium_on_Ubuntu",
	"installing apertium on linux": "http://wiki.apertium.org/wiki/Apertium_on_Ubuntu",
	"installing apertium on windows": "http://wiki.apertium.org/wiki/Apertium_on_Windows",
	"google summer of code": "http://wiki.apertium.org/wiki/Google_Summer_of_Code",
	"gsoc": "http://wiki.apertium.org/wiki/Google_Summer_of_Code",
	"spectie": "http://wiki.apertium.org/wiki/User:Francis_Tyers",
	"firespeaker": "http://wiki.apertium.org/wiki/User:Firespeaker",
	"zfe": "http://quotes.firespeaker.org/?who=zfe"
	}

def breaklong(phr):
    line = phr
    li = []
    maxchars = 300
    while line != '':
        extra = ""
        if len(line) > maxchars:
            extra = line[maxchars:]
            line = line[:maxchars]
        li.append(line)
        line = extra
    return li

buff = []

def information(phenny, input):
	""".information (<topic>) get information on a topic"""
	global topics

	topic = input.group(2)

	if topic.lower() in topics:
		phenny.say(topics[topic.lower()])
	else:
		phenny.say("Sorry, no information on %s is currently available ☹")

information.name = 'information'
information.commands = ['information']
information.example = '.information (installing apertium)'
information.priority = 'low'


def randquote(phenny, input):
    """.randquote (<topic>) - Get a random quote from quotes.firespeaker.org (about topic)."""
    global buff
    buff = []
    topic = input.group(2)

    # create opener
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-agent', web.Grab().version),
        ('Referer', "http://quotes.firespeaker.org/"),
    ]
    maxlen = 20000

    try:
        if topic == "" or topic==None:
            req = opener.open("http://quotes.firespeaker.org/random.php?maxlen=%s" % (maxlen))
        else:
            req = opener.open("http://quotes.firespeaker.org/random.php?maxlen=%s&topic=%s" % (maxlen,web.quote(topic)))
        data = req.read().decode('utf-8')
        data = json.loads(data)
    except (HTTPError, IOError, ValueError):
        raise GrumbleError(
                "Firespeaker.org down?  Try again later.")

    if len(data) == 0:
        phenny.say("No results found")
        return

    #result = data['list'][0]
    #url = 'http://www.urbandictionary.com/define.php?term={0}'.format(web.quote(word))
    #
    #response = "{0} - {1}".format(result['definition'].strip()[:256], url)

    if data['quote'] != None:
        quote = data['quote'].replace('</p>', '').replace('<p>', '').replace('\n', '  ').replace('<em>', '_').replace('</em>', '_').replace('&mdash;', '—')
        response = data['short_url'] + ' - ' + quote
        broke = breaklong(response)
        if isinstance(broke, list):
            buff.extend(broke)
        else:
            buff.append(broke)
        res = buff.pop()
        if buff:
            res += ' ({0} more messages)'.format(len(buff))
    else:
        phenny.say("Sorry, no quotes returned!")
        return

    phenny.say(res)

randquote.name = 'randquote'
randquote.commands = ['randquote']
randquote.example = '.randquote (linguistics)'
randquote.priority = 'low'

def more(phenny, input):
    global buff
    if buff:
        res = buff.pop()
        if buff:
            res += ' ({0} more messages)'.format(len(buff))
        phenny.say(res)
        return

more.name = 'more'
more.commands = ['more']
more.example = '.more'
more.priority = 'low'
#urbandict.rule = (['urb'], r'(.*)')

if __name__ == '__main__':
    print(__doc__.strip())
