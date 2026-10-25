#!/usr/bin/python3
"""
weirdfun.py - activities that weird people do
author: firespeaker <firespeaker@firespeaker.org>
"""

import random
from bot import command

otherweird = "zfe"

@command('fight', priority='low', example='.fight ChanServ')
def fight(phenny, msg):
    """Have begiak fight someone for you."""
    global otherweird
    whouser = msg.command_args
    already = False
    if whouser:
        otherweird = whouser
        if whouser.lower()==phenny.nick.lower():
            already = True
            phenny.say("ouch!")

    #### "hits %s", "punches %s", "kicks %s",, "stabs %s with a clean kitchen knife",  "hits %s with a rubber hose",
    messages = [ "hurts himself by accident while trying to attack %s", "directs his Öflazers at %s", "is bored of violence against %s", "thinks you should talk it over with %s first", "cocks %s's beer", "eats %s's hat", "sets %s up the bomb"]
    response = random.choice(messages)

    if not already:
        phenny.do(response % otherweird)

@command('hug', priority='low', example='.hug ChanServ')
def hug(phenny, msg):
    """Have begiak hug someone for you."""
    global otherweird
    whouser = msg.command_args
    if whouser:
        otherweird = whouser

    if not whouser:
        phenny.do('tries to hug himself but fails.')
    elif whouser.lower()==phenny.nick.lower():
        phenny.do("tries but fails.")
    else:
        phenny.do("hugs %s" % otherweird)

if __name__ == '__main__':
    print(__doc__.strip())
