#!/usr/bin/python3
"""
language.py - Query Wikidata for language data
author: popcorndude, scoopgracie
"""

from lxml.etree import ElementTree
import web
import json
from bot import command

def shorten_num(n):
    if n < 1000:
        return '{:,}'.format(n)
    elif n < 1000000:
        return '{}K'.format(str(round(n/1000, 1)).rstrip('0').rstrip('.'))
    else:
        return '{}M'.format(str(round(n/1000000, 1)).rstrip('0').rstrip('.'))

@command(['wikidata', 'lg'], example='.lg khk')
def lang(phenny, msg):
    """.lang <lg> - gives Wikidata info from partial language name or iso639"""
    raw = msg.command_args.lower()
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
        pop_query = '''
SELECT ?language ?languageLabel ?population ?speaker_type ?speaker_typeLabel ?date
WHERE
{
  ?language p:P1098 ?statement.
  ?statement ps:P1098 ?population.
  ?language wdt:P220 "%s".
  OPTIONAL { ?statement pq:P518 ?speaker_type }
  OPTIONAL { ?statement pq:P585 ?date }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY DESC(?date)
''' % iso[0]
        loc_query = '''
SELECT ?language ?languageLabel ?country ?countryLabel ?population
WHERE {
  ?language wdt:P220 "%s".
  ?language wdt:P17 ?country.
  ?country wdt:P1082 ?population.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY DESC(?population)
''' % iso[0]
        try:
            pop_req = web.get('https://query.wikidata.org/sparql', params={'query': pop_query, 'format': 'json'})
            pop_data = json.loads(pop_req)
        except web.HTTPError as e:
            phenny.say('Oh noes! Wikidata responded with ' + str(e.code) + ' ' + e.msg)
            pop_data = {'results': {'bindings': []}}
        try:
            loc_req = web.get('https://query.wikidata.org/sparql', params={'query': loc_query, 'format': 'json'})
            loc_data = json.loads(loc_req)
        except web.HTTPError as e:
            phenny.say('Oh noes! Wikidata responded with ' + str(e.code) + ' ' + e.msg)
            loc_data = {'results': {'bindings': []}}
        if len(pop_data['results']['bindings']) + len(loc_data['results']['bindings']) == 0:
            phenny.say("No information found for {} ({}) on Wikidata.".format(phenny.ethno_data[iso[0]], iso[0]))
            return
        pop_total = None
        pop_l1 = None
        pop_l2 = None
        for entry in pop_data['results']['bindings']:
            value = shorten_num(int(entry['population']['value']))
            if 'speaker_typeLabel' in entry:
                if entry['speaker_typeLabel']['value'] == 'first language':
                    if pop_l1 == None:
                        pop_l1 = value
                elif entry['speaker_typeLabel']['value'] == 'second language':
                    if pop_l2 == None:
                        pop_l2 = value
            elif pop_total == None:
                pop_total = value
        if pop_total == None and pop_l1 == None and pop_l2 == None:
            pop_str = ''
        elif pop_total != None:
            pop_str = 'with %s total speakers' % pop_total
            if pop_l1 != None and pop_l2 != None:
                pop_str += ' (%s L1, %s L2)' % (pop_l1, pop_l2)
            elif pop_l1 != None:
                pop_str += ' (%s L1)' % pop_l1
            elif pop_l2 != None:
                pop_str += ' (%s L2)' % pop_l2
        else:
            ls = []
            if pop_l1 != None:
                ls.append('%s L1' % pop_l1)
            if pop_l2 != None:
                ls.append('%s L2' % pop_l2)
            pop_str = ' and '.join(ls) + ' speakers'
        if pop_str:
            pop_str = ' ' + pop_str
        countries = [entry['countryLabel']['value'] for entry in loc_data['results']['bindings']]
        if len(countries) > 5:
            countries = countries[:5] + ['and others']
        elif len(countries) == 0:
            countries = ['[location data unavailable]']
        link = (pop_data['results']['bindings'] + loc_data['results']['bindings'])[0]['language']['value']
        response = "{} ({}) is a language of {}{}. Source: {}".format(phenny.ethno_data[iso[0]], iso[0], ', '.join(countries), pop_str, link)
    elif len(iso) > 1:
        did_you_mean = ['{} ({})'.format(i, phenny.ethno_data[i]) for i in iso if len(i) == 3]
        response = "Try .iso639 for better results. Did you mean: " + ', '.join(did_you_mean) + "?"
    else:
        response = "That ISO code wasn't found. (Hint: use .iso639 for better results)"

    phenny.say(response)
