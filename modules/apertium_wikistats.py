#!/usr/bin/env python3
"""
apertium_wikistats.py - Phenny Apertium Wiki Stats Module
"""

import os
import requests
import shlex
import subprocess
from web import REQUEST_TIMEOUT, head
from requests import HTTPError
from tools import dot_path
from bot import command
PARENT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT = os.path.join(PARENT_DIRECTORY, 'apertium_wikistats_bot.py')
BOT_AUTOCOVERAGE = ('/bot_autocoverage.py', 'bot_autocoverage.py')
AUTOCOVERAGE = os.path.join(PARENT_DIRECTORY, 'autocoverage.py')

IS_COVERAGE_RUNNING = ''

@command('awikstats', example='.awikstats update tat, kaz, tat-kaz or .awikstats coverage tyv', priority='high')
def awikstats(phenny, msg):
    """Issue commands to the Apertium Stem Counter Bot."""

    if (not hasattr(phenny.config, 'stemCounterBotLogin') or
        not hasattr(phenny.config, 'stemCounterBotPassword')):
        phenny.say('Bot login/password needs to be set in configuration file (default.py).')
        phenny.say('Keys are stemCounterBotLogin and stemCounterBotPassword.')
        return

    botLogin = phenny.config.stemCounterBotLogin
    botPassword = phenny.config.stemCounterBotPassword

    if not msg.command_args:
        phenny.say('Invalid .awikstats command; try something like .awikstats update tat, kaz, tat-kaz')
        return

    option = msg.command_args_list[0]

    if option == 'update':
        try:
            langs = ''.join(msg.command_args_list[1:]).split(',')
        except:
            phenny.say('Invalid .awikstats update command; try something like %s' % repr(awikstats.example_update))
            return

        commands = shlex.split('python3 %s %s "%s" dict -p %s -r "%s"' % (BOT, botLogin, botPassword, ' '.join(langs), msg.nick))
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dot_path(''))
        stdout, stderr = process.communicate()

        for line in stderr.splitlines():
            phenny.msg(msg.nick, line)
    elif option == 'coverage':
        global IS_COVERAGE_RUNNING

        if IS_COVERAGE_RUNNING == '':
            try:
                lang = msg.command_args_list[1]
            except:
                phenny.say('Invalid .awikstats coverage command; try something like %s' % repr(awikstats.example_coverage))
                return

            try:
                head('https://wiki.apertium.org/wiki/Apertium-' + lang)
            except HTTPError:
                phenny.say('%s: No wiki for specified language!' % msg.nick)
                return

            phenny.say('%s: Calculating coverage... It may take a while, I will inform you after it\'s completed.' % msg.nick)

            commands = shlex.split('python3 %s %s "%s" coverage -p %s -r "%s"' % (BOT, botLogin, botPassword, lang, msg.nick))
            IS_COVERAGE_RUNNING = lang
            process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dot_path(''))
            stdout, stderr = process.communicate()
            IS_COVERAGE_RUNNING = ''

            try:
                out = stdout.splitlines()[-1].decode('utf-8').strip()
                if out.startswith('Coverage:'):
                    phenny.msg(msg.nick, '%s - https://wiki.apertium.org/wiki/Apertium-%s/stats' % (out, lang))
                else:
                    for line in stderr.splitlines():
                        phenny.msg(msg.nick, line)
            except:
                for line in stderr.splitlines():
                    phenny.msg(msg.nick, line)
        else:
            phenny.say('%s: Sorry, there is already %s coverage running, try again after it\'s completed!' % (msg.nick, IS_COVERAGE_RUNNING))
    else:
        phenny.say('Invalid .awikstats option: %s' % option)
        return
