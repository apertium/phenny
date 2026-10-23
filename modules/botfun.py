#!/usr/bin/python3
"""
botfun.py - activities that bots do
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from bot import command
import random

otherbot = "ChanServ"

@command('botfight', ping=False, priority='low')
def botfight(phenny, msg):
    """.botfight - Fight the other bot in the channel."""

    messages = ["hits %s", "punches %s", "kicks %s", "hits %s with a rubber hose", "stabs %s with a clean kitchen knife"]
    response = random.choice(messages)

    phenny.do(response % otherbot)

@command('bothug', ping=False, priority='low')
def bothug(phenny, msg):
    """.bothug - Hug the other bot in the channel."""
    phenny.do("hugs %s" % otherbot)

if __name__ == '__main__':
    print(__doc__.strip())
