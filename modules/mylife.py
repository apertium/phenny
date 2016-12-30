#!/usr/bin/python3
"""
mylife.py - various commentary on life
author: Ramblurr <unnamedrambler@gmail.com>
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import GrumbleError
import web
import lxml.html
from random import choice


def fml(phenny, input):
    """.fml - Grab something from fmylife.com."""
    try:
        req = web.get("http://www.fmylife.com/random")
    except:
        raise GrumbleError("I tried to use .fml, but it was broken. FML")

    doc = lxml.html.fromstring(req)
    quote = choice(doc.find_class('fmllink')).text_content().strip()
    phenny.say(quote)
fml.commands = ['fml']


def mlia(phenny, input):
    """.mlia - My life is average."""
    try:
         req = web.get("http://mylifeisaverage.com/")
    except:
        raise GrumbleError("I tried to use .mlia, but it wasn't loading. MLIA")

    doc = lxml.html.fromstring(req)
    quote = choice(doc.find_class('story')).text_content().strip()
    phenny.say(quote)
mlia.commands = ['mlia']


if __name__ == '__main__':
    print(__doc__.strip())
