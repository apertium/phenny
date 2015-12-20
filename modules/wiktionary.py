#!/usr/bin/env python
"""
wiktionary.py - Phenny Wiktionary Module
Copyright 2009, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web
import json
import re, urllib.request, urllib.parse, urllib.error

uri = 'http://en.wiktionary.org/wiki/{0}?printable=yes'
wikiapi = 'http://en.wiktionary.org/w/api.php?action=query&titles={0}&prop=revisions&rvprop=content&format=json'
wikisearchapi = 'http://en.wiktionary.org/w/api.php?action=query&list=search&srlimit=1&format=json&srsearch={0}'
#r_tag = re.compile(r'<[^>]+>')
r_ul = re.compile(r'(?ims)<ul>.*?</ul>')
r_li = re.compile(r'^# ')
r_img = re.compile(r'\[\[Image:.*\]\]')
r_link1 = re.compile(r'\[\[([A-Za-z0-9\-_ ]+?)\]\]')
r_link2 = re.compile(r'\[\[([A-Za-z0-9\-_ ]+?)\|(.+?)\]\]')
r_context = re.compile(r'{{context\|(.+?)}}')
r_template1 = re.compile(r'{{.+?\|(.+?)}}')
r_template2 = re.compile(r'{{(.+?)}}')
r_sqrbracket = re.compile(r'\[.+?\]')

def text(html): 
    text = r_li.sub('', html).strip()
    text = r_img.sub('', text)
    text = r_link1.sub(r'\1', text)
    text = r_link2.sub(r'\2', text)
    text = r_context.sub(r'\1:', text)
    text = r_template1.sub(r'\1:', text)
    text = r_template2.sub(r'\1:', text)
    text = text.replace("en|", '')
    text = r_sqrbracket.sub('', text)
    return text

def wiktionary(phenny, word): 
    bytes = web.get(wikiapi.format(web.quote(word)))
    pages = json.loads(bytes)
    pages = pages['query']['pages']
    pg = next(iter(pages))

    try:
        result = pages[pg]['revisions'][0]['*']
    except KeyError:
        return '', ''

    mode = None
    etymology = None
    definitions = {}
    for line in result.splitlines(): 
        if line == '===Etymology===':
            mode = 'etymology'
        elif '=Noun=' in line: 
            mode = 'noun'
        elif '=Verb=' in line: 
            mode = 'verb'
        elif '=Adjective=' in line: 
            mode = 'adjective'
        elif '=Adverb=' in line: 
            mode = 'adverb'
        elif '=Interjection=' in line: 
            mode = 'interjection'
        elif '=Particle=' in line: 
            mode = 'particle'
        elif '=Preposition=' in line: 
            mode = 'preposition'
        elif mode == 'etymology':
            etymology = text(line)
        
        if mode is not None and "#" in line and "#:" not in line:
            definitions.setdefault(mode, []).append(text(line))

        if '====Synonyms====' in line: 
            break

    return etymology, definitions
    
def get_between(strSource, strStart, strEnd): #get first string between 2 other strings
    try:
        parse = strSource.split(strStart, 2)[1]
        parse = parse[:parse.find(strEnd)]
    except:
        parse = None
    return parse 

def get_between_all(strSource, strStart, strEnd): #get all the strings between the 2 strings
    list = []
    start = 0
    word = get_between(strSource, strStart, strEnd)
    while (word != None):
        list.append(word)
        start = strSource.find("".join((strStart, word, strEnd)))
        strSource = strSource[start+len("".join((strStart, word, strEnd))):]
        word = get_between(strSource, strStart, strEnd)
    return list

def etymology(phenny, word):
    ety_value = None
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17')]
        bytes = opener.open(uri.format(web.quote(word)))
        html = bytes.read().decode('utf-8')
        ety_value = get_between_all(html, '">Etymology</span></h3>', '</p>')
        ety_value = " ".join(ety_value)
        ety_value = re.compile(r'<[^<]*?/?>').sub('', ety_value)
        ety_value = ety_value.replace('&#160;', '')
        ety_value = ety_value.replace('From ', '← ')
        ety_value = ety_value.replace(', from', ' ←')
        ety_value = ety_value.replace('from ', '← ')
        ety_value = word + ": " + ety_value.replace(".", '') + "."
        ety_value = r_sqrbracket.sub('', ety_value)
        
        if len(ety_value) > 300:
            ety_value = ety_value[:295] + " [...]"
    except:
        ety_value = None
    return ety_value


parts = ('preposition', 'particle', 'noun', 'verb', 
    'adjective', 'adverb', 'interjection')

def format(word, definitions, number=2): 
    result = '%s' % word
    for part in parts: 
        if part in definitions: 
            defs = definitions[part][:number]
            result += ' \u2014 ' + ('%s: ' % part)
            n = ['%s. %s' % (i + 1, e.strip(' .')) for i, e in enumerate(defs)]
            result += ', '.join(n)
    return result.strip(' .,')


def wikitionary_lookup(phenny, word, to_user=None):
    etymology, definitions = wiktionary(phenny, word)

    if definitions:
        result = format(word, definitions)
        if len(result) < 150: 
            result = format(word, definitions, 3)
        if len(result) < 150: 
            result = format(word, definitions, 5)
            
        result = result.replace('|_|', ' ').replace('|', ' ')

        if len(result) > 300: 
            result = result[:295] + '[...]'
        if to_user:
            phenny.say(to_user+", "+result)
        else:
            phenny.say(result)
    else:
        apiResponse = json.loads(str(web.get(wikisearchapi.format(word))))
        if len(apiResponse['query']['search']):
            word = apiResponse['query']['search'][0]['title']
            phenny.say("Perhaps you meant %s?" % repr(word))
        else:
            phenny.say("Couldn't find any definitions for %s." % word)


def w(phenny, input): 
    """Look up a word on Wiktionary."""
    if not input.group(2):
        return phenny.reply("Nothing to define.")
    word = input.group(2)

    if "->" in word: return
    if "→" in word: return

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(word)
    if matched_point:
        to_nick = matched_point.groups()[0]
        word2 = matched_point.groups()[1]
        
        wikitionary_lookup(phenny, word2, to_user=to_nick)
        return


    wikitionary_lookup(phenny, word)

w.rule = r'\.(w)\s(.*)'
w.example = '.w bailiwick or nick: .w bailiwick or .w bailiwick -> nick'+\
            ' or .w point nick bailiwick'


def w2 (phenny, input):
    nick, _, __, lang, word = input.groups()
    wikitionary_lookup(phenny, word, to_user=nick)


w2.rule = r'(\S*)(:|,)\s\.(w)(\.[a-z]{2,3})?\s(.*)'
w2.example = 'svineet: .w Seppuku'


def w3(phenny, input):
    _, lang, word, __, nick = input.groups()
    wikitionary_lookup(phenny, word, to_user=nick)

w3.rule = r'\.(w)(\.[a-z]{2,3})?\s(.*)\s(->|→)\s(\S*)'
w3.example = '.w Seppuku -> svineet'


def ety(phenny, input): 
    """Find the etymology of a word."""
    if not input.group(2):
        return phenny.reply("Nothing to define.")
    word = input.group(2)
    ety_val = ''
    ety_val = etymology(phenny, word)
    if not ety_val or ety_val == word + ' .': 
        phenny.say("Couldn't get any etymology for %s." % word)
        return
    phenny.say(text(ety_val))
ety.commands = ['ety']
ety.example = '.ety bailiwick'

if __name__ == '__main__': 
    print(__doc__.strip())
