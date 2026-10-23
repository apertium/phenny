#!/usr/bin/python3
"""
iso639.py - ISO codes module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import random
import web
from bot import command

template = "{} = {}"

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

@command('iso639', priority='low', example='.iso639 khk')
def iso639(phenny, msg):
    """.iso639 <lg> | .iso639 <Language> - Search ISO 639-1, -2 and -3 for a language code."""
    response = ""
    thisCode = msg.command_args.lower()
    if not thisCode:
        thisCode = random.choice(list(phenny.iso_data.keys()))
        #ISOcodes[random.randint(0,len(ISOcodes)-1)]
        #random.choice(ISOcodes)
    else:
        if len(thisCode) > 3:      # so that we don't get e.g. 'a'
            for oneCode, oneLang in phenny.iso_data.items():
                if thisCode in flatten(oneLang.lower()):
                    if response != "":
                        response += ", " + template.format(oneCode, oneLang)
                    else:
                        response = template.format(oneCode, oneLang)
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
            response = template.format(thisCode + (", " + altCode if altCode else ""), phenny.iso_data[thisCode])

    if response == "":
        response = "Sorry, %s not found" % thisCode

    phenny.say(response)

def scrape_iso_codes(phenny):
    # see https://iso639-3.sil.org/code_tables/download_tables
    # for more information
    iso = {}
    ethno = {}
    convert = {}
    codes = web.get('https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3.tab')
    for entry in codes.splitlines()[1:]:
        values = entry.split('\t')
        code3 = values[0]
        code2b = values[1]
        code2t = values[2]
        code1 = values[3]
        name = values[6]
        values = entry.split('\t')
        if code2b:
            iso[code2b] = name
        if code2t:
            iso[code2t] = name
        if code1:
            iso[code1] = name
            convert[code1] = code3
            convert[code3] = code1
        iso[code3] = name
        ethno[code3] = name
    phenny.ethno_data = ethno
    phenny.iso_data = iso
    phenny.iso_conversion_data = convert

@command('isodb_update', admin=True)
def refresh_database(phenny, msg):
    scrape_iso_codes(phenny)
    phenny.say('ISO code database successfully written')

def setup(phenny):
    scrape_iso_codes(phenny)

if __name__ == '__main__':
    print(__doc__.strip())
