#!/usr/bin/python3
"""
nsfw.py - some things just aren't safe for work, a phenny module
author: Casey Link <unnamedrambler@gmail.com
"""

from bot import command

@command('nsfw')
def nsfw(phenny, msg):
    """.nsfw <link> - Mark a link (or some text) as being not safe for work."""
    if not msg.command_args:
        phenny.say(".nsfw <link> - for when a link isn't safe for work")
    else:
        phenny.say("!!NSFW!! -> %s <- !!NSFW!!" % (msg.command_args))

if __name__ == '__main__':
    print(__doc__.strip())
