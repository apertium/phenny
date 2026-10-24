#!/usr/bin/env python
"""
info.py - Phenny Information Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

from bot import command, COMMANDS
import collections

@command(['help', 'command'])
def help(phenny, msg):
    command = msg.command_args

    # work out a help URL to display
    try:
        helpurl = phenny.config.helpurl
    except AttributeError:
        helpurl = "https://wiki.apertium.org/wiki/Begiak"

    if msg.sender.startswith('#'):
        # channels get a brief message instead
        phenny.say(
            "Hey there, I'm a friendly bot for #apertium. Say \".help\" "
            "to me in private for a list of my commands or check out my help "
            "page at {helpurl}.".format(helpurl=helpurl))
    elif command:
        command = command.lower()
        if command in COMMANDS:
            func = COMMANDS[command]
            if func.__doc__:
                phenny.say(func.__doc__.strip())
                if hasattr(func, 'example'):
                    phenny.say('e.g. ' + func.example)
            else:
                phenny.say("Sorry, I don't know how to use that command.")
        else:
            phenny.say("Sorry, I don't know that command.")
    else:
        command_names = ', '.join(sorted(COMMANDS.keys()))
        phenny.say(
            "Hey there, I'm a friendly bot! Here are the commands I "
            "recognize: {commands}".format(commands=command_names))
        phenny.say(
            "For help with a command, just use .help followed by the name of"
            " the command, like \".help botsnack\".")
        phenny.say(
            "If you need additional help can check out {helpurl} or you can "
            "talk to my owner, {owner}.".format(
            helpurl=helpurl,
            owner=phenny.config.owner))

@command('stats')
def stats(phenny, msg):
    """Show information on command usage patterns."""
    commands = collections.Counter()
    users = collections.Counter()
    channels = collections.Counter()

    ignore = set(['startup', 'message', 'note_and_snarf_uri', 'logger',
        'checkMessages', 'measure', 'messageAlert'])
    for (name, user), count in list(phenny.stats.items()):
        if name in ignore: continue
        if not user: continue
        if user == phenny.nick: continue

        if not user.startswith('#'):
            users[user] += count
        else:
            commands[name] += count
            channels[user] += count

    # most heavily used commands
    creply = 'most used commands: '
    creply += ', '.join('%s (%s)' % x for x in commands.most_common(10))
    phenny.say(creply)

    # most heavy users
    reply = 'power users: '
    reply += ', '.join('%s (%s)' % x for x in users.most_common(10))
    phenny.say(reply)

    # most heavy channels
    chreply = 'power channels: '
    chreply += ', '.join('%s (%s)' % x for x in channels.most_common(3))
    phenny.say(chreply)

if __name__ == '__main__':
    print(__doc__.strip())
