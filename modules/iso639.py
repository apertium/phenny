#!/usr/bin/python3
"""
iso639.py - ISO codes module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

#from tools import GrumbleError
import random
from modules.ethnologue import setup as ethno_setup
from modules.ethnologue import write_ethnologue_codes
from lxml import html
import web
import os
import threading
import re

template = "%s = %s"

def flatten(s):
    #match against accented characters
    my_copy = str(s)
    flatten_mapping = {
        'a': 'áäâ',
        'e': 'éè',
        'i': 'íî',
        'o': 'óö',
        'u': 'ùüú',
        'n': 'ñ',
        "'": '’'
    }
    for i in my_copy:
        for k, v in flatten_mapping.items():
            if i in v:
                my_copy = my_copy.replace(i, k)

    return my_copy


def iso639(phenny, input):
    """.iso639 <lg> | .iso639 <Language> - Search ISO 639-1, -2 and -3 for a language code."""
    response = ""
    thisCode = str(input.group(2)).lower()
    if thisCode == "None":
        thisCode = random.choice(list(phenny.iso_data.keys()))
        #ISOcodes[random.randint(0,len(ISOcodes)-1)]
        #random.choice(ISOcodes)
    else:
        if len(thisCode) > 3:      # so that we don't get e.g. 'a'
            for oneCode, oneLang in phenny.iso_data.items():
                if thisCode in flatten(oneLang.lower()):
                    if response != "":
                        response += ", " + template % (oneCode, oneLang)
                    else:
                        response = template % (oneCode, oneLang)
                    #phenny.say("%s %s %s" % (oneCode, oneLang.lower(), thisCode.lower()))
        elif thisCode in phenny.iso_data:
            altCode = None
            if len(thisCode) == 2 and thisCode in phenny.iso_conversion_data:
                altCode = phenny.iso_conversion_data[thisCode]
            elif len(thisCode) == 3:
                for iso1, iso3 in phenny.iso_conversion_data.items():
                    if thisCode == iso3:
                        altCode = iso1
                        break
            response = template % (thisCode + (", " + altCode if altCode else ""), phenny.iso_data[thisCode])

    if response == "":
        response = "Sorry, %s not found" % thisCode

    phenny.say(response)

def scrape_wiki_codes():
    data = {}
    base_url = 'http://en.wikipedia.org/wiki/List_of_ISO_639'
    #639-1
    resp = web.get(base_url + '-1_codes')
    h = html.document_fromstring(resp)
    table = h.find_class('wikitable')[0]
    for row in table.findall('tr')[1:]:
        name = row.findall('td')[2].find('a').text
        code = row.findall('td')[4].text
        data[code] = name
    #639-2
    resp = web.get(base_url + '-2_codes')
    h = html.document_fromstring(resp)
    table = h.find_class('wikitable')[0]
    for row in table.findall('tr')[1:]:
        name = row.findall('td')[3].find('a')
        if name:
            name = name.text
        else:
            continue
        code_list = row.findall('td')[0].text.split(' ')
        if len(code_list) == 1:
            code = code_list[0]
        else:
            for i in code_list:
                if '*' in i:
                    code = i.replace('*', '')
                    break
        data[code] = name

    return data

def scrape_wiki_codes_convert():
    data = {}
    base_url = 'http://en.wikipedia.org/wiki/List_of_ISO_639'
    #639-1
    resp = web.get(base_url + '-1_codes')
    h = html.document_fromstring(resp)
    table = h.find_class('wikitable')[0]
    for row in table.findall('tr')[1:]:
        iso3code = row.findall('td')[7].text
        code = row.findall('td')[4].text
        if iso3code:
            r = re.match("(.*) \+ .*", iso3code)
            if r:
                iso3code = r.group(1)
            data[iso3code] = code
            data[code] = iso3code

    return data

def iso_filename(phenny):
    name = phenny.nick + '-' + phenny.config.host + '.iso-codes.db'
    return os.path.join(os.path.expanduser('~/.phenny'), name)

def iso_one_to_three_filename(phenny):
    name = phenny.nick + '-' + phenny.config.host + '.iso-codes-conversion.db'
    return os.path.join(os.path.expanduser('~/.phenny'), name)

def write_dict(filename, data):
    with open(filename, 'w', encoding="utf-8") as f:
        for k, v in data.items():
            f.write('{}${}\n'.format(k, v))

def read_dict(filename):
    data = {}
    with open(filename, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            if line == '\n':
                continue
            code, name = line.replace('\n', '').split('$')
            data[code] = name
    return data

def refresh_database(phenny, raw=None):
    if raw.admin or raw is None:
        f = iso_filename(phenny)
        write_ethnologue_codes(phenny)
        phenny.iso_data = scrape_wiki_codes()
        phenny.iso_data.update(phenny.ethno_data)
        write_dict(f, phenny.iso_data)
        phenny.say('ISO code database successfully written')

        f2 = iso_one_to_three_filename(phenny)
        phenny.iso_conversion_data = scrape_wiki_codes_convert()
        write_dict(f2, phenny.iso_conversion_data)
        phenny.say('ISO conversion db successfully written')
    else:
        phenny.say('Only admins can execute that command!')

def thread_check(phenny, raw):
    for t in threading.enumerate():
        if t.name == refresh_database.name:
            phenny.say('An ISO code updating thread is currently running')
            break
    else:
        phenny.say('No ISO code updating thread running')

def setup(phenny):
    ethno_setup(phenny) #populate ethnologue codes
    f = iso_filename(phenny)
    if os.path.exists(f):
        try:
            phenny.iso_data = read_dict(f)
        except ValueError:
            print('iso database read failed, refreshing it')
            phenny.iso_data = scrape_wiki_codes()
            phenny.iso_data.update(phenny.ethno_data)
            write_dict(f, phenny.iso_data)
    else:
        phenny.iso_data = scrape_wiki_codes()
        phenny.iso_data.update(phenny.ethno_data)
        write_dict(f, phenny.iso_data)

    # Conversion hash
    f2 = iso_one_to_three_filename(phenny)
    if os.path.exists(f2):
        try:
            phenny.iso_conversion_data = read_dict(f2)
        except ValueError:
            print('iso conversion db read failed, refreshing it')
            phenny.iso_conversion_data = scrape_wiki_codes_convert()
            write_dict(f2, phenny.iso_conversion_data)
    else:
        phenny.iso_conversion_data = scrape_wiki_codes_convert()
        write_dict(f2, phenny.iso_conversion_data)


iso639.name = 'iso639'
#iso639.rule = (['iso639'], r'(.*)')
iso639.commands = ['iso639']
iso639.example = '.iso639 khk'
iso639.priority = 'low'

refresh_database.name = 'refresh_iso_database'
refresh_database.commands = ['isodb update']
refresh_database.thread = True

thread_check.name = 'iso_thread_check'
thread_check.commands = ['isodb status']

if __name__ == '__main__':
    print(__doc__.strip())
