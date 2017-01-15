#!/usr/bin/env python
"""
apertium_wiki.py - Phenny Wikipedia Module
"""

import re
import web
import json
from lxml import etree
import lxml.html
import lxml.html.clean
from modules.posted import check_posted

wikiuri = 'http://wiki.apertium.org/wiki/{:s}'
wikisearchuri = 'http://wiki.apertium.org/api.php?action=query&list=search&srlimit=1&format=json&srsearch={:s}&srwhat={:s}'
LOGS_URL = "http://tinodidriksen.com/pisg/freenode/logs/"


def format_term(term):
    term = web.quote(term)
    term = term[0].upper() + term[1:]
    term = term.replace(' ', '_')
    return term


def format_term_display(term):
    term = web.unquote(term)
    term = term[0].upper() + term[1:]
    term = term.replace(' ', '_')
    return term


def format_subsection(section):
    section = section.replace(' ', '_')
    section = web.quote(section)
    section = section.replace('%', '.')
    return section


def apertium_wiki(phenny, input, origterm, to_nick=None):
    term = format_term(origterm)

    try:
        html = str(web.get(wikiuri.format(term)))
    except:
        apiResponse = json.loads(str(web.get(wikisearchuri.format(term, 'title'))))
        if len(apiResponse['query']['search']):
            term = apiResponse['query']['search'][0]['title']
            html = str(web.get(wikiuri.format(term)))
        else:
            apiResponse = json.loads(str(web.get(wikisearchuri.format(term, 'text'))))
            if len(apiResponse['query']['search']):
                term = apiResponse['query']['search'][0]['title']
                html = str(web.get(wikiuri.format(term)))
            else:
                phenny.reply("No wiki results for that term.")
                return

    page = lxml.html.fromstring(html)

    if "#" in origterm:
        section = format_subsection(origterm.split("#")[1])
        text = page.find(".//span[@id='%s']" % section)
        if text is None:
            phenny.reply("That subsection does not exist.")
            return
        text = text.getparent().getnext()
    else:
        paragraphs = page.findall('.//p')
        if len(paragraphs) > 2:
            text = page.findall('.//p')[1]
        else:
            text = page.findall(".//*[@id='mw-content-text']")[0]

    sentences = text.text_content().split(". ")
    sentence = '"' + sentences[0] + '"'

    maxlength = config.maxlength - len((' - ' + wikiuri.format(format_term_display(term))).encode('utf-8'))
    if len(sentence.encode('utf-8')) > maxlength:
        sentence = sentence.encode('utf-8')[:maxlength].decode('utf-8', 'ignore')
        words = sentence[:-5].split(' ')
        words.pop()
        sentence = ' '.join(words) + ' [...]'

    if hasattr(input, 'sender'):
        check_posted(phenny, input, wikiuri.format(format_term_display(term)))
    if to_nick:
        phenny.say(to_nick + ', ' + sentence + ' - ' + wikiuri.format(format_term_display(term)))
    else:
        phenny.say(sentence + ' - ' + wikiuri.format(format_term_display(term)))


def awik(phenny, input):
    """Search for something on Apertium wiki or
    point another user to a page on Apertium wiki (supports pointing)"""
    origterm = input.groups()[1]

    if "->" in origterm or "→" in origterm:
        return

    if not origterm:
        return phenny.say('Perhaps you meant ".wik Zen"?')

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(origterm)
    to_nick = None
    if matched_point:
        to_nick = matched_point.groups()[0]
        origterm = matched_point.groups()[1]

    apertium_wiki(phenny, input, origterm, to_nick=to_nick)


awik.rule = r'\.(awik)\s(.*)'
awik.example = '.awik Begiak or .awik point nick Begiak or .awik Begiak -> nick' ' or nick: .awik Begiak'
awik.priority = 'high'


def awik2(phenny, input):
    nick, _, __, lang, origterm = input.groups()
    apertium_wiki(phenny, input, origterm, nick)


awik2.rule = r'(\S*)(:|,)\s\.(awik)(\.[a-z]{2,3})?\s(.*)'
awik2.example = 'svineet: .awik Begiak'
awik2.priority = 'high'


def awik3(phenny, input):
    _, lang, origterm, __, nick = input.groups()
    apertium_wiki(phenny, input, origterm, nick)


awik3.rule = r'\.(awik)(\.[a-z]{2,3})?\s(.*)\s(->|→)\s(\S*)'
awik3.example = '.awik Linguistics -> svineet'


def logs(phenny, input):
    """ Shows logs URL """

    phenny.say("Logs at %s" % LOGS_URL)

logs.commands = ['logs', 'log']
logs.priority = 'low'
logs.example = '.logs'
