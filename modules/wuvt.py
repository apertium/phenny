#!/usr/bin/env python
"""
wuvt.py - WUVT now playing module for phenny
"""

import web


def wuvt(phenny, input):
    """.wuvt - Find out what is currently playing on the radio station WUVT."""

    data = web.get('https://www.wuvt.vt.edu/playlists/latest_track',
                   headers={'Accept': "application/json"})
    trackinfo = web.json(data)

    if 'listeners' in trackinfo:
        phenny.say(
            "{dj} is currently playing \"{title}\" by {artist} with "
            "{listeners:d} online listeners".format(
                dj=trackinfo['dj'],
                title=trackinfo['title'],
                artist=trackinfo['artist'],
                listeners=trackinfo['listeners']))
    else:
        phenny.say("{dj} is currently playing \"{title}\" by {artist}".format(
            dj=trackinfo['dj'],
            title=trackinfo['title'],
            artist=trackinfo['artist']))
wuvt.commands = ['wuvt']
wuvt.example = '.wuvt'
