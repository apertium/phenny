#!/usr/bin/python3
"""
botsnack.py - .botsnack module (aka simulated hunger 1.0)
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
author: Casey Link <unnamedrambler@gmail.com>

This module simulates bot hunger and provides a mechanism
for users to feed the bot.

To prevent abuse when the bot gets very, very full, it explodes
and enters a random cooldown period for 3-10 minutes. When in this
cooldown period all calls to botsnack are ignored.
"""

import logging
import math
import random
import time
from bot import command, keyword

logger = logging.getLogger('phenny')

# the rate that affects how much eating a snack nourishes the bot
# smaller number = less nourishment = more snacks can be eaten (before fullness)
# larger number = more nourishment = fewer snacks can be eaten
r_eat = 0.05

# the rate that affects how fast the bot becomes hungry over time
# smaller number = the bot gets hungry slower
# larger number = the bot gets hungry faster
r_hunger = 0.005

def increase_hunger(current_hunger, x):
    # more hungry === value closer to 0
    return current_hunger * math.exp(-r_hunger * x)

def decrease_hunger(current_hunger, food_value):
    # less hungry === closer to 100
    if current_hunger > 50: # exponential growth
        return min(100, current_hunger * math.exp(r_eat*food_value))
    else: # linear increase
        return current_hunger + food_value

hunger = 50
last_tick = time.time()
coolingdown = False

@command('botsnack')
def botsnack(phenny, msg):
    """.botsnack - Feed me a bot snack."""

    global hunger, last_tick, coolingdown

    now = time.time()

    # 0. Handle cooldown.
    #    Check if the cooldown period has elapsed, if not, then
    #    ignore this invocation. Else reset to the default state
    if coolingdown:
        if now - coolingstarted > coolingperiod:
            logger.debug("cooling down over, reseting")
            coolingdown = False
            hunger = 50.0
            last_tick = now
        else:
            logger.debug("cooling down! %s < %s" %(now - coolingstarted, coolingperiod))
            return # ignore!

    # 1. Time has has passed, so the bot has gotten
    #    hungry. Lets increase his/her hunger proportionate
    #    to the amount of time that has passeed.
    delta = now - last_tick
    old_hunger = hunger

    hunger = increase_hunger(old_hunger, delta)

    logger.debug("hunger was %s, increased to %s" %(old_hunger, hunger))

    last_tick = now

    # 2. Eat some food. Send resposne

    old_hunger = hunger
    hunger = decrease_hunger(old_hunger, random.uniform(1,5))
    logger.debug("hunger was %s, decreased to %s" %(old_hunger, hunger))

    if hunger > 95: # special case to prevent abuse
        phenny.say("Too much food!")
        phenny.do("explodes")
        coolingperiod = random.uniform(3,10)*60
        coolingstarted = now
        coolingdown = True
    elif hunger > 90:
        messages = ["I don't think this will fit...", "Ugh, no more please", "Seriously, I can't eat anymore!", "/me shudders but downs the snack anyways"]
    elif hunger > 70:
        messages = ["Thanks, but that's enough", "If you insist"]
    elif hunger > 50:
        messages = ["Om nom nom", "Delicious, thanks!", "Yummy!", "Wow! That's delicious"]
    elif hunger > 30:
        messages = ["That really hit the spot!", "/me smacks lips", "Mmmmm!"]
    elif hunger > 10:
        messages = ["Awww yea, that was tasty", "/me munches rudely"]
    elif hunger > 1:
        messages = ["/me noms furiously", "I really needed that!"]
    else:
        messages = ["I'M STARVING. GIVE ME MORE!", "/me gnaws ravenously on the snack with a starved look"]

    msg = random.choice(messages)
    if msg.startswith("/me "):
        phenny.do(msg.partition("/me ")[2])
    else:
        phenny.say(msg)

@command(['botslap', 'botsmack'])
def botslap(phenny, msg):
    """tell me I'm being a bad bot"""
    messages = ["hides in corner", "eats own hat", "apologises", "stares at feet", "points at zfe", "didn't do anything", "doesn't deserve this", "hates you guys", "did it on purpose", "is an inconsistent sketchy little bot", "scurries off"]
    phenny.do(random.choice(messages))

@keyword(r'''^(?:(?:$nickname[ ,:]?)\s+(you suck|I hate you|you ruin everything|you spoil all [themyour]*fun|bad|wtf|lame| [youare']*?stupid|silly)\s*$)|(?:.*?(you suck|I hate you|you ruin everything|you spoil all [themyour]*fun|bad|wtf|lame|[youare']*?stupid|silly)(?:[, ]?))''')
def botslap2(phenny, msg):
    if phenny.nick in msg.text:
        botslap(phenny, msg)

if __name__ == '__main__':
    print(__doc__.strip())
