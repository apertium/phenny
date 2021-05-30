#!/usr/bin/env python
"""
info.py - Phenny Information Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""


def help(phenny, input):
    command = input.group(1)

    # work out a help URL to display
    try:
        helpurl = phenny.config.helpurl
    except AttributeError:
        helpurl = "https://wiki.apertium.org/wiki/Begiak"

    commands = [func for priority, commands in phenny.commands.items()
            for regex, funcs in commands.items() for func in funcs]

    if input.sender.startswith('#'):
        # channels get a brief message instead
        phenny.say(
            "Hey there, I'm a friendly bot for #apertium. Say \".help\" "
            "to me in private for a list of my commands or check out my help "
            "page at {helpurl}.".format(helpurl=helpurl))
    elif command:
        command = command.lower()
        if command in phenny.doc:
            phenny.say(phenny.doc[command][0].strip())
            if phenny.doc[command][1]: 
                phenny.say('e.g. ' + phenny.doc[command][1])
        elif any(func.name == command for func in commands):
            phenny.say("Sorry, I don't know how to use that command.")
        else:
            phenny.say("Sorry, I don't know that command.")
    else:
        command_names = ', '.join(sorted(command.name for command in commands))
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
help.rule = (['help', 'command'], r'(.*)')
help.priority = 'low'


def stats(phenny, input): 
    """Show information on command usage patterns."""
    commands = {}
    users = {}
    channels = {}

    ignore = set(['startup', 'message', 'noteuri', 'logger',
        'snarfuri', 'measure', 'messageAlert'])
    for (name, user), count in list(phenny.stats.items()): 
        if name in ignore: continue
        if not user: continue

        if not user.startswith('#'): 
            try: users[user] += count
            except KeyError: users[user] = count
        else: 
            try: commands[name] += count
            except KeyError: commands[name] = count

            try: channels[user] += count
            except KeyError: channels[user] = count

    comrank = sorted([(b, a) for (a, b) in commands.items()], reverse=True)
    userank = sorted([(b, a) for (a, b) in users.items()], reverse=True)
    charank = sorted([(b, a) for (a, b) in channels.items()], reverse=True)

    # most heavily used commands
    creply = 'most used commands: '
    for count, command in comrank[:10]: 
        creply += '%s (%s), ' % (command, count)
    phenny.say(creply.rstrip(', '))

    # most heavy users
    reply = 'power users: '
    for count, user in userank[:10]: 
        reply += '%s (%s), ' % (user, count)
    phenny.say(reply.rstrip(', '))

    # most heavy channels
    chreply = 'power channels: '
    for count, channel in charank[:3]: 
        chreply += '%s (%s), ' % (channel, count)
    phenny.say(chreply.rstrip(', '))
stats.commands = ['stats']
stats.priority = 'low'


if __name__ == '__main__':
    print(__doc__.strip())
