#!/usr/bin/python3
"""
linx.py - linx.li tools
author: andreim <andreim@andreim.net>
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import GrumbleError
import web
import json


def linx(phenny, input, short=False):
    """.linx <url> - Upload a remote URL to linx.li."""

    url = input.group(2)
    if not url:
        phenny.reply("No URL provided. CAN I HAS?")
        return

    try:
        req = web.post("https://linx.li/upload/remote", {'url': url, 'short': short, 'api_key': phenny.config.linx_api_key})
    except (web.HTTPError, web.ConnectionError):
        raise GrumbleError("Couldn't reach linx.li")

    data = json.loads(req)
    if len(data) <= 0 or not data['success']:
        phenny.reply('Sorry, upload failed.')
        return

    phenny.reply(data['url'])
linx.rule = (['linx'], r'(.*)')


def lnx(phenny, input):
    """
    same as .linx but returns a short url.
    """
    linx(phenny, input, True)
lnx.rule = (['lnx'], r'(.*)')
