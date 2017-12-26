#!/usr/bin/env python3
"""
apertium_wiki.py - Phenny Apertium Wiki Stats Module
"""

import requests, subprocess, shlex, os

BOT = ('https://svn.code.sf.net/p/apertium/svn/trunk/apertium-tools/wiki-tools/bot.py', 'apertium_wikistats_bot.py')
LEXCCOUNTER = ('https://svn.code.sf.net/p/apertium/svn/trunk/apertium-tools/lexccounter.py', 'lexccounter.py')

def filename(name):
    return os.path.join(os.path.expanduser('~/.phenny'), name)

def setup(phenny):
    for files in [BOT, LEXCCOUNTER]:
        r = requests.get(files[0])
        if r.status_code == 200:
            with open(filename(files[1]), 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)

def awikstats(phenny, input):
    """Issue commands to the Apertium Stem Counter Bot."""

    botPassword = phenny.config.stemCounterBotPassword
    if botPassword is None:
        phenny.say('Bot password not set; set it in default.py')
        return

    try:
        rawInput = input.group()
        option = rawInput.split(' ')[1].strip()
    except:
        phenny.say('Invalid .awikstats command; try something like %s' % repr(awikstats.example))
        return

    if option == 'update':
        try:
            langs = ''.join(rawInput.split(' ')[2:]).split(',')
        except:
            phenny.say('Invalid .awikstats update command; try something like %s' % repr(awikstats.example))
            return

        commands = shlex.split('python3 %s StemCounterBot "%s" dict -p %s -r "%s"' % (BOT[1], botPassword, ' '.join(langs), input.nick))
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=filename(''))
        stdout, stderr = process.communicate()

        for line in stderr.splitlines():
            phenny.msg(input.nick, line)
    else:
        phenny.say('Invalid .awikstats option: %s' % option)
        return

awikstats.commands = ['awikstats']
awikstats.example = '.awikstats update tat, kaz, tat-kaz'
awikstats.priority = 'high'
