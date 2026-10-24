#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
choose.py - sometimes you just can't decide, a phenny module
"""

import random
import re
from bot import command

@command('choose')
def choose(phenny, msg):
    """.choose <red> <blue> - for when you just can't decide"""
    if not msg.command_args:
        return phenny.say(".choose <red> <blue> - for when you just can't decide")
    fate = random.choice(msg.command_args.replace(',', ' ').split())
    return phenny.reply(fate)

if __name__ == '__main__':
    print(__doc__.strip())
