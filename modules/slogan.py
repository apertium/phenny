#!/usr/bin/env python
"""
slogan.py - Phenny Slogan Module
Copyright (c) 2011 Dafydd Crosby - http://www.dafyddcrosby.com

Licensed under the Eiffel Forum License 2.
"""

from tools import GrumbleError
import re
import web
import urllib.request

uri = 'http://www.sloganizer.net/en/outbound.php?slogan='

headers = [(
    'User-Agent', 'Mozilla/5.0' +
    '(X11; U; Linux i686)' +
    'Gecko/20071127 Firefox/2.0.0.11'
)]

def sloganize(word): 
    opener = urllib.request.build_opener()
    opener.addheaders = headers
    response = opener.open(uri + word).read()
    response = response.decode('utf-8')
    return response

def slogan(phenny, input): 
    """.slogan <term> - Come up with a slogan for a term."""

    word = input.group(2)
    if word is None:
        phenny.say("You need to specify a word; try .slogan Granola")
        return
    
    word = word.strip()
    slogan = sloganize(word)

    # Remove HTML tags    
    remove_tags = re.compile(r'<.*?>')
    slogan = remove_tags.sub('', slogan)
    if not slogan:
        raise GrumbleError("Looks like an issue with sloganizer.net")
    phenny.say(slogan)
slogan.commands = ['slogan']
slogan.example = '.slogan Granola'

if __name__ == '__main__': 
    print(__doc__.strip())
