#!/usr/bin/python3
"""
ethnologue.py - Ethnologue.com language lookup
author: mattr555
"""

from lxml import html
from string import ascii_lowercase
import web
import logging

logger = logging.getLogger('phenny')

def shorten_num(n):
    if n < 1000:
        return '{:,}'.format(n)
    elif n < 1000000:
        return '{}K'.format(str(round(n/1000, 1)).rstrip('0').rstrip('.'))
    elif n < 1000000000:
        return '{}M'.format(str(round(n/1000000, 1)).rstrip('0').rstrip('.'))

def scrape_ethnologue_codes(phenny):
    data = {}
    base_url = 'https://www.ethnologue.com/browse/codes/'
    for letter in ascii_lowercase:
        resp = web.get(base_url + letter, cache=True)
        h = html.document_fromstring(resp)
        for e in h.find_class('views-field-field-iso-639-3'):
            code = e.find('div/a').text
            name = e.find('div/a').attrib['title']
            data[code] = name
    phenny.ethno_data = data

def write_ethnologue_codes(phenny, raw=None):
    if raw is None or raw.admin:
        scrape_ethnologue_codes()
        logger.debug('Ethnologue iso-639 code fetch successful')
        if raw:
            phenny.say('Ethnologue iso-639 code fetch successful')
    else:
        phenny.say('Only admins can execute that command!')

write_ethnologue_codes.name = 'write_ethnologue_codes'
write_ethnologue_codes.commands = ['write-ethno-codes']
write_ethnologue_codes.priority = 'low'

def parse_num_speakers(s):
    hits = []
    for i in s.split(' '):
        if len(i) <= 3 or ',' in i:
            if i.replace(',', '').replace('.', '').isdigit():
                hits.append(int(i.replace(',', '').replace('.', '')))
    if hits and 'no known l1 speakers' in s.lower():
        return 'No primary'
    elif hits and 'ethnic population' in s.lower() or 'l2 users worldwide' in s.lower():
        return shorten_num(sorted(hits, reverse=True)[1])
    elif hits:
        return shorten_num(max(hits))
    return 'No primary'

def ethnologue(phenny, input):
    """.ethnologue <lg> - gives ethnologue info from partial language name or iso639"""
    raw = str(input.group(2)).lower()
    iso = []
    if len(raw) == 3 and raw in phenny.ethno_data:
        iso.append(raw)
    elif len(raw) == 2 and raw in phenny.iso_conversion_data:
        iso.append(phenny.iso_conversion_data[raw])
    elif len(raw) > 3:
        for code, lang in phenny.ethno_data.items():
            if raw in lang.lower():
                iso.append(code)

    if len(iso) == 1:
        url = "http://www.ethnologue.com/language/" + iso[0]
        try:
            resp = web.get(url)
        except web.HTTPError as e:
            phenny.say('Oh noes! Ethnologue responded with ' + str(e.code) + ' ' + e.msg)
            return
        h = html.document_fromstring(resp)

        if "macrolanguage" in h.find_class('field-name-a-language-of')[0].find('div/div/h2').text:
            name = h.get_element_by_id('page-title').text
            iso_code = h.find_class('field-name-language-iso-link-to-sil-org')[0].find('div/div/a').text
            num_speakers_field = h.find_class('field-name-field-population')[0].find('div/div/p').text
            num_speakers = parse_num_speakers(num_speakers_field)
            child_langs = map(lambda e:e.text[1:-1], h.find_class('field-name-field-comments')[0].findall('div/div/p/a'))
            response = "{} ({}) is a macrolanguage with {} speakers and the following languages: {}. Src: {}".format(
                name, iso_code, num_speakers, ', '.join(child_langs), url)
        else:
            name = h.get_element_by_id('page-title').text
            iso_code = h.find_class('field-name-language-iso-link-to-sil-org')[0].find('div/div/a').text
            where_spoken = h.find_class('field-name-a-language-of')[0].find('div/div/h2/a').text
            where_spoken_cont = h.find_class('field-name-field-region')
            if where_spoken_cont:
                where_spoken_cont = where_spoken_cont[0].find('div/div/p').text[:100]
                if len(where_spoken_cont) > 98:
                    where_spoken_cont += '...'
                where_spoken += ', ' + where_spoken_cont
            if where_spoken[-1] != '.':
                where_spoken += '.'
            num_speakers_field = h.find_class('field-name-field-population')[0].find('div/div/p').text
            num_speakers = parse_num_speakers(num_speakers_field)
            language_status = h.find_class('field-name-language-status')[0].find('div/div/p').text.split('.')[0] + '.'

            response = "{} ({}): spoken in {} {} speakers. Status: {} Src: {}".format(
                name, iso_code, where_spoken, num_speakers, language_status, url)
    elif len(iso) > 1:
        did_you_mean = ['{} ({})'.format(i, phenny.ethno_data[i]) for i in iso if len(i) == 3]
        response = "Try .iso639 for better results. Did you mean: " + ', '.join(did_you_mean) + "?"
    else:
        response = "That ISO code wasn't found. (Hint: use .iso639 for better results)"

    phenny.say(response)

ethnologue.name = 'ethnologue'
ethnologue.commands = ['ethnologue', 'ethno', 'logue', 'lg', 'eth']
ethnologue.example = '.ethnologue khk'
ethnologue.priority = 'low'

def setup(phenny):
    scrape_ethnologue_codes(phenny)
