#!/usr/bin/env python

"""
eleda.py - Begiak Eleda Module
Any questions can go to Qasim Iqbal (nick: Qasim) (email: me@qas.im)
"""

import json
import web
from modules import caseless_equal, apy

follows = []

class Eleda(object):
    def __init__(self, sender, nick, dir):
        self.sender = sender # follower
        self.nick = nick # followed
        self.dir = dir

def follow(phenny, input):
    """Follow someone and translate as they speak."""

    # TODO: what if the nick is not present in the channel?
    # phenny possibly informs sender that the nick is not present and continues?

    global follows

    try:
        nick, dir, *extra = input.group(1).split(' ')
        dir = tuple(dir.split('-'))
        _ = dir[1]
    except:
        phenny.reply("Need nick and language pair!")
        return

    if caseless_equal(nick, phenny.config.nick):
        phenny.reply(phenny.config.nick.upper() + " DOES NOT LIKE TO BE FOLLOWED.")
        return

    try:
        apy_url = self.phenny.config.APy_url
    except:
        apy_url = 'https://beta.apertium.org/apy'

    response = json.loads(web.get(apy_url + '/listPairs'))
    pairs = response["responseData"]

    if {"targetLanguage": dir[1], "sourceLanguage": dir[0]} not in pairs:
        try:
            dir[0] = phenny.iso_conversion_data[dir[0]]
            dir[1] = phenny.iso_conversion_data[dir[1]]
        except:
            phenny.reply("That language pair does not exist!")
            return

        if {"targetLanguage": dir[1], "sourceLanguage": dir[0]} not in pairs:
            phenny.reply("That language pair is not supported!")
            return

    # only accept follower paramter if it exists and the nick is admin
    if len(extra) >= 1 and input.admin:
        sender = extra[0]
    else:
        sender = input.nick

    for i in follows:
        if caseless_equal(i.nick, nick) and i.dir == dir and caseless_equal(i.sender, sender):
            phenny.say("%s is already following %s with %s." % (sender, nick, '-'.join(dir)))
            return

    follows.append(Eleda(sender, nick, dir))
    phenny.reply("%s now following %s (%s)." % (sender, nick, '-'.join(dir)))

follow.commands = ['follow']
follow.example = '.follow Qasim en-es'

def unfollow(phenny, input):
    """Stop following someone."""

    global follows

    target = input.group(1)

    for i in follows:
        if not (caseless_equal(i.nick, target) and caseless_equal(i.sender, input.nick)):
            continue

        follows.remove(i)
        phenny.reply(target + " is no longer being followed.")
        return

    phenny.reply("Sorry, you aren't following that user!")

unfollow.commands = ['unfollow']
unfollow.example = '.unfollow Qasim'

def following(phenny, input):
    """List people currently being followed."""

    text = []

    for i in follows:
        text.append('%s (%s) by %s' % (i.nick, '-'.join(i.dir), i.sender))

    if text:
        phenny.say("Currently followed: " + ", ".join(text) + ". (Translations are private)")
    else:
        phenny.reply("No one is being followed at the moment.")

following.commands = ['following']
following.example = '.following'

def checkMessages(phenny, input):
    '''filter through each message in the channel'''

    if input.sender not in phenny.channels:
        return

    text = input.group(0)

    # don't translate commands
    if text.startswith('.'):
        return

    translations = {}

    for i in follows:
        if not caseless_equal(i.nick, input.nick):
            continue

        # this user is being followed, translate them

        try:
            translation = translations[(i.nick, i.dir)]
        except:
            direction = '-'.join(i.dir)
            translation = apy.translate(phenny, text, i.dir[0], i.dir[1])
            translation = translation.replace('*', '')
            translations[(i.nick, i.dir)] = translation

        # don't send translation if the input is the same as the output
        if translation == text:
            continue

        phenny.msg(i.sender, '%s (%s): %s' % (i.nick, '-'.join(i.dir), translation))

checkMessages.rule = r'(.*)'
