#!/usr/bin/env python
"""
away.py - Phenny's record or who's away/present module
"""

from bot import command

statuses = {"alan": "boom bitchezzzz"}

@command('whereis', example='.whereis sushain')
def whereis(phenny, msg):
    """Tells you nick's current status."""
    whereis_nick = msg.command_args
    if (whereis_nick.casefold() in list(statuses.keys())):
        phenny.reply(whereis_nick + " said: " + statuses[whereis_nick.casefold()])
    else:
        phenny.reply("Sorry, " + whereis_nick + " seems to be AWOL...")

@command('away', example='.away eating pie')
def away(phenny, msg):
    """Set your status to being away."""
    nick = msg.nick.casefold()
    statuses[nick] = msg.command_args or "I'm away right now"

@command('back')
def back(phenny, msg):
    """Set your status to being available."""
    nick = input.nick.casefold()
    statuses[nick] = msg.command_args or "I'm around at the minute"

if __name__ == '__main__':
    print(__doc__.strip())
