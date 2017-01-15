#!/usr/bin/env python
"""
wikipedia.py - Phenny Wikipedia Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re, urllib.parse, wiki
from lxml import etree
import lxml.html
import lxml.html.clean
import web
from modules.posted import check_posted

wikiapi = 'https://%s.wikipedia.org/w/api.php?action=query&list=search&srsearch={0}&limit=1&prop=snippet&format=json'
wikiuri = 'https://%s.wikipedia.org/wiki/{0}'
wikisearch = 'https://%s.wikipedia.org/wiki/Special:Search?' \
                          + 'search={0}&fulltext=Search'

langs = ['ar', 'bg', 'ca', 'cs', 'da', 'de', 'en', 'es', 'eo', 'eu', 'fa', 'fr', 'ko', 'hi', 'hr', 'id', 'it', 'he', 'lt', 'hu', 'ms', 'nl', 'ja', 'no', 'pl', 'pt', 'kk', 'ro', 'ru', 'sk', 'sl', 'sr', 'fi', 'sv', 'tr', 'uk', 'vi', 'vo', 'war', 'zh']


def format_term(term):
    term = web.unquote(term)
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
   section = urllib.parse.quote_plus(section)
   section = section.replace('%', '.')
   section = section.replace(".3A", ":")
   return section

def parse_wiki_page(url, term, section = None):
    try:
        web_url = web.quote(url).replace("%3A", ":", 1)
        html = str(web.get(web_url))
    except:
        return "A wiki page does not exist for that term."
    page = lxml.html.fromstring(html)
    if section is not None:
        text = page.find(".//span[@id='%s']" % section)

        if text is None:
            return "That subsection does not exist."
        text = text.getparent().getnext()

        #a div tag may come before the text
        while text.tag is not None and text.tag != "p":
            text = text.getnext()
        url += "#" + format_term_display(section)
    else:
        #Get first paragraph

        text = page.get_element_by_id('mw-content-text').find('p')

    sentences = text.text_content().split(". ")   
    sentence = '"' + sentences[0] + '"'

    maxlength = config.maxlength - len((' - ' + url).encode('utf-8'))
    if len(sentence.encode('utf-8')) > maxlength: 
        sentence = sentence.encode('utf-8')[:maxlength].decode('utf-8', 'ignore')
        words = sentence[:-5].split(' ')
        words.pop()
        sentence = ' '.join(words) + ' [...]'

    return sentence + ' - ' + url

def wikipedia(phenny, input, origterm, lang, to_user = None):
    origterm = origterm.strip()
    lang = lang.strip()

    if not origterm: 
        return phenny.say('Perhaps you meant ".wik Zen"?')
    
    section = None

    if "#" in origterm:
        origterm, section = origterm.split("#")[:2]
        section = format_subsection(section)
    term = format_term(origterm)

    w = wiki.Wiki(wikiapi % lang, wikiuri % lang, wikisearch % lang)

    try:
        result = w.search(term)
    except web.ConnectionError:
        error = "Can't connect to en.wikipedia.org ({0})".format(wikiuri.format(term))
        return phenny.say(error)

    if result is not None: 
        #Disregarding [0], the snippet
        url = result.split("|")[-1]
        check_posted(phenny, input, url)
        if to_user:
            phenny.say(to_user + ', ' + parse_wiki_page(url, term, section))
        else:
            phenny.say(parse_wiki_page(url, term, section))
    else:
        phenny.say('Can\'t find anything in Wikipedia for "{0}".'.format(origterm))


def point_to(phenny, input, origterm, lang, nick):
    wikipedia(phenny, input, origterm, lang, to_user=nick)


def wik(phenny, input): 
    """Search for something on Wikipedia (supports pointing)"""
    if "->" in input.group(3): return
    if "→" in input.group(3): return

    origterm = input.group(3)
    if input.group(2):
        lang = input.group(2)[1:]
    else:
        lang = "en"

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(origterm)
    if matched_point:
        to_nick = matched_point.groups()[0]
        origterm2 = matched_point.groups()[1]
        
        point_to(phenny, input, origterm2, lang, to_nick)
        return
    
    wikipedia(phenny, input, origterm, lang)

wik.rule = r'\.(wik|wiki|wikipedia)(\.[a-z]{2,3})?\s(.*)'
wik.priority = 'low'
wik.example = '.wik Human or nick: .wik Human or .wik Human -> nick'+\
            ' or .wik point nick Human'


def wik2(phenny, input):
    nick, _, __, lang, origterm = input.groups()
    if not lang: lang = "en"

    point_to(phenny, input, origterm, lang, nick)

wik2.rule = r'(\S*)(:|,)\s\.(wik|wiki|wikipedia)(\.[a-z]{2,3})?\s(.*)'
wik2.priority = 'high'
wik2.example = 'svineet: .wik Linguistics'


def wik3(phenny, input):
    _, lang, origterm, __, nick = input.groups()
    if not lang: lang = "en"

    point_to(phenny, input, origterm, lang, nick)

wik3.rule = r'\.(wik|wiki|wikipedia)(\.[a-z]{2,3})?\s(.*)\s(->|→)\s(\S*)'
wik3.priority = 'high'
wik3.example = '.wik Linguistics -> svineet'


def pointing(phenny, input):
    """ Begiak also supports pointing users to the output of other commands.
    For example, .wik India -> nick will make Begiak say:
    nick, "India, officially the Republic of India (Bhārat Gaṇarājya),
    [18][19][c] is a country in South Asia" - https://en.wikipedia.org/wiki/India 
    . Do .awik Begiak for more information on supported commands.
    """
    pass

pointing.commands = ['pointing']


if __name__ == '__main__': 
    print(__doc__.strip())
