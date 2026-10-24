#!/usr/bin/env python
# coding=utf-8
"""
calc.py - Phenny Calculator Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import sympy
import re
from bot import command

@command('c', example='.c 5 + 3')
def c(phenny, msg):
    if not msg.command_args:
        return phenny.reply("Nothing to calculate.")
    calc = msg.command_args

    if '=' in calc:
        calc = calc.replace(' ', '')
        calc = re.sub(r"((?:\d+)|(?:[a-zA-Z]\w*\(\w+\)))((?:[a-zA-Z]\w*)|\()", r"\1*\2", calc)

        left, right = calc.split('=')
        calc = left + '-(' + right + ')'
        try:
            result = sympy.solve(calc)
        except:
            return phenny.say('Sorry, no result.')

    else:
        try:
            result = sympy.sympify(calc)
        except:
            return phenny.say('Sorry, no result.')

    res = ''
    more = False
    if type(result) is list and len(result) > 1:
        if type(result[0]) is not dict:
            more = True
            for element in result:
                res += str(sympy.N(element)) + ', '
            res = res[:-2]
            res = '[' + res + ']'
    elif type(result) is list and len(result) == 1:
        result = result[0]

    if more is not True:
        try:
            result = str(float(result))
            if result.endswith('.0'):
                result = str(int(float(result)))
        except:
            result = str(result)
            if result.isalpha():
                return phenny.say('Sorry, no result.')

        if result:
            phenny.say(result)
        else:
            return phenny.say('Sorry, no result.')
    else:
        phenny.say(res)

if __name__ == '__main__':
    print(__doc__.strip())
