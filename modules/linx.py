#!/usr/bin/python3
"""
linx.py - linx.li tools
author: andreim <andreim@andreim.net>
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import GrumbleError
import requests
import json


def linx(phenny, input, short=False):
    """.linx <url> - Upload a remote URL to linx.li."""

    url = input.group(2)

    if not url:
        phenny.reply("No URL provided")
        return

    r = requests.get("https://linx.vtluug.org/upload?", params={"url": url}, headers={"Accept": "application/json"})

    if "url" in r.json():
        phenny.reply(r.json()["url"])
    else:
        phenny.reply(r.json()["error"])
linx.rule = (['linx'], r'(.*)')
