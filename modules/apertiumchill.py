#!/usr/bin/python3
"""
chillmeter.py - .chill measures chill level of the channel
author: Casey Link <unnamedrambler@gmail.com>
author: mutantmonkey <mutantmonkey@mutantmonkey.in>

so chill bro.
"""
import random, time


# chill decay rate per minute
chill_decay_rate = 5

chill_words = [
    # words that make the place chill
    ("chill", 1),
    ("bro", 1),
    ("fist bump", 2),
    ("fistbump", 2),
    ("natty", 1),
    ("natties", 2),
    ("head nod", 1),
    ("she said", 1),
    ("keystone", 1),
    ("sandwich", 1),
    ("lax", 2),
    ("lacrosse", 2),
    ("pinny", 2),
    ("bowl", 1),
    ("slampiece", 2),
    ("smirnoff", 1),
    ("ices", 1),
    ("iced", 1),
    ("longboard", 2),
    ("boning", 1),
    ("orange", 1),
    ("maroon", 1),
    ("kicks", 1),
    ("dome", 1),
    ("69", 1),
    ("bang", 1),
    ("COD", 2),
    ("blazed", 1),
    ("man", 1),    # apertium additions here down
    ("awesome", 1),
    ("nice", 1),
    ("rock", 1),
    ("works!", 2),
    (":D", 1),
    ("heh", 1),
    ("food", 1),
    ("mantı", 2),
    ("manty", 2),
    ("manti", 2),
    ("Volga", 2),
    ("Shupashkar", 2),
    ("ayran", 2),

    # words that unchill the place
    ("dude", -1),
    ("suck", -2),
    ("desi", -1),
    ("lame", -2),
    ("imageshack", -1),
    ("microsoft", -1),
    ("btreecat", -1),
    ("homework", -1),
    ("project", -2),
    ("test", -2),
    ("exam", -2),
    ("4chan", -1),
    ("digg", -1),
    ("work", -1),
    ("unchill", -2),
    ("asshole", -2),   # apertium additions here down
    ("assignment", -2),
    ("stop", -1),
    ("idiot", -1),
    ("Öflazer", -2),
    ("NO EXCEPTIONS", -1),
]

# all things chill
chill_things = [
    #("natty", "natties"),
    #("smirnoff ice", "smirnoffs"),
    #("bong hit", "bong hits"),
    #("case of keystone", "cases of keystone"),
    #("fist bump", "fist bumps"),
    #("head nod", "head nods"),
    #("bro", "bros"),
    #("bowl", "bowls")
    ("manty", "manty"),
    ("ayran", "ayrans"),
    ("ale", "ales"),
    ("ice skating", "ice skating"),
    ("dip in the Volga", "dips in the Volga"),
    ("trip to Shupashkar", "trips to Shupashkar")
]

# keeps a finger on the pulse of the chillness
def measure(phenny, input):
    chill = measure.channels.get(input.sender, 0)
    now = time.time()
    if now - measure.last_tick > 60:
        measure.last_tick = now
        if chill > 0:
            chill -= chill_decay_rate
            chill = max(0, chill)
        elif chill < 0:
            chill += chill_decay_rate
            chill = min(0, chill)
        measure.channels[input.sender] = chill

    if ".chill" in input:
        return # dont self count

    for w in chill_words:
        if w[0] in input.lower():
            chill += w[1]

    measure.channels[input.sender] = chill


measure.rule = r'.*'
measure.priority = 'low'
measure.last_tick = time.time()
measure.channels = {}

def chill(phenny, input):
    """.chill - Measure the current channel chillness level."""
    level = measure.channels.get(input.sender, 0)

    n = random.randint(1,2)
    items = []
    used = set()
    for i in range(n):
        if level == 0:
            amount = random.randint(5, 10)
        elif level < 0:
            amount = random.randint(10, -level * 2 + 10)
        else:
            amount = random.randint(1, level)
        item = random.choice(chill_things)

        while item in used:
            item = random.choice(chill_things)
        used.add(item)

        if amount == 1:
            item = item[0] # singular
        else:
            item  = item[1] # plural
        items.append("%s %s" % (amount, item))

    item_str = ", ".join(items)
    #print level, item_str

    if level <= 0:
        message = "WARNING: CHILL LEVEL IS DANGEROUSLY LOW. RECOMMEND %s" % (item_str.upper())
    else:
        message = "chill level is currently: %s" % (item_str)

    phenny.say(message)


chill.commands = ['chill']
chill.priority = 'low'

if __name__ == '__main__':
    print(__doc__.strip())
