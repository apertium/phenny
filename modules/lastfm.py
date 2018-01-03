#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
lastfm.py - lastfm module
author: Casey Link <unnamedrambler@gmail.com>
"""

import random
import configparser
import os
import web
from lxml import etree
from datetime import datetime
from tools import db_path

APIKEY = "816cfe50ddeeb73c9987b85de5c19e71"
APIURL = "https://ws.audioscrobbler.com/2.0/?api_key="+APIKEY+"&"

config = configparser.RawConfigParser()
config.optionxform = str
config_filename = ""

def setup(self):
    global config_filename
    config_filename = db_path(self, 'lastfm')
    if not os.path.exists(config_filename):
        try: f = open(config_filename, 'w')
        except OSError: pass
        else:
            f.write('')
            f.close()

    config_file = config.read(config_filename)
    if not config.has_section("Nick2User"):
        config.add_section("Nick2User")
    if not config.has_section("User2Nick"):
        config.add_section("User2Nick")
    if not config.has_section("Nick2Verb"):
        config.add_section("Nick2Verb")

def lastfm_set(phenny, input):
    cmd = input.group(2)
    caseless_nick = input.nick.casefold()
    if not cmd or len(cmd.strip()) == 0:
        phenny.say("commands: user, verb")
        phenny.say("set <username>: associates your IRC nick with your last.fm username.")
        phenny.say("example: lastfm-set user joebob")
        phenny.say("verb <past>,<present>: customizes the verbs used when displaying your now playing info.")
        phenny.say("example: lastfm-set verb listened to, is listening to")
        return
    if cmd == "user":
        value = input.group(5)
        if len(value) == 0:
            phenny.say("um.. try again. the format is 'lastfm-set user username'")
            return
        set_username(caseless_nick, value)
        phenny.say("ok, i'll remember that %s is %s on lastfm" % (input.nick, value))
        return
    if cmd == "verb":
        past = input.group(3)
        present = input.group(4)
        if len(past) == 0 or len(present) == 0:
            phenny.say("umm.. try again. the format is 'lastfm-set verb past phrase, present phrase' example: 'lastfm-set verb listened to, listening to'")
            return
        set_verb(caseless_nick, past, present)
        phenny.say("ok, i'll remember that %s prefers '%s' and '%s'" % (input.nick, past, present))
        return

lastfm_set.rule = (['lastfm-set'], r'(\S+)\s+(?:(.*?),(.*)|(\S+))')

def now_playing(phenny, input):
    nick = input.nick.casefold()
    user = ""
    arg = input.group(2)
    if not arg or len(arg.strip()) == 0:
        user = resolve_username(nick) # use the sender
        if not user: #nick didnt resolve
            user = nick
    else: # use the argument
        user = resolve_username(arg.strip())
        if not user: # user didnt resolve
            user = arg
    user = user.strip()
    try:
        req = web.get("%smethod=user.getrecenttracks&user=%s" % (APIURL, web.quote(user)))
    except web.HTTPError as e:
        if e.response.status_code == 400:
            phenny.say("%s doesn't exist on last.fm, perhaps they need to set user" % (user))
            return
        else:
            phenny.say("uhoh. try again later, mmkay?")
            return
    root = etree.fromstring(req.encode('utf-8'))
    recenttracks = list(root)
    if len(recenttracks) == 0:
        phenny.say("%s hasn't played anything recently. this isn't you? try lastfm-set" % (user))
        return
    tracks = list(recenttracks[0])
    #print(etree.tostring(recenttracks[0]))
    if len(tracks) == 0:
        phenny.say("%s hasn't played anything recently. this isn't you? try lastfm-set" % (user))
        return
    first = tracks[0]
    now = True if first.get("nowplaying") == "true" else False
    tags = {}
    for e in first.getiterator():
        tags[e.tag] = e

    track = tags['name'].text.strip()

    artist = tags['artist'].text.strip()

    album = "unknown"
    if tags['album'].text:
        album = tags['album'].text

    date = None
    stamp = None
    if not now:
        date = tags['date'].get("uts")
        stamp = int(date)

    if now:
        present = get_verb(nick)[1]
        phenny.say("%s %s \"%s\" by %s on %s" %(user.strip(), present.strip(), track, artist, album ))
        return
    else:
        past = get_verb(nick)[0]
        phenny.say("%s %s \"%s\" by %s on %s %s" %(user.strip(), past.strip(), track, artist, album, pretty_date(stamp)))

now_playing.commands = ['np']

def save_config():
    configfile  = open(config_filename, 'w')
    config.write(configfile)
    configfile.close()

def set_verb(nick, past, present):
    verbs = "%s,%s" % (past,present)
    config.set("Nick2Verb", nick, verbs )
    save_config()

def get_verb(nick):
    if config.has_option("Nick2Verb", nick):
        return config.get("Nick2Verb", nick).split(',')
    return ["listened to","is listening to"]

def set_username(nick, username):
    old_user = resolve_username(nick)
    if old_user:
        config.remove_option("User2Nick", old_user)
    config.set("Nick2User", nick, username)
    config.set("User2Nick", username, nick)
    save_config()

def resolve_username(nick):
    if config.has_option("Nick2User", nick):
        return config.get("Nick2User", nick)
    return None

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff // 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff // 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"

if __name__ == '__main__':
    print(__doc__.strip())
