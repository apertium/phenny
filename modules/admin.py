#!/usr/bin/env python
"""
admin.py - Phenny Admin Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import os
import re
import subprocess

from modules import reload

from bot import command, event

def check_return(command):
    try:
        subprocess.check_call(command)
        return True
    except subprocess.CalledProcessError:
        return False

def get_output(command):
    try:
        return subprocess.check_output(command)
    except subprocess.CalledProcessError:
        return None

def check_signature(message, signature):
    return check_return(['./ssh/verify-msg.sh'] + message + [signature])

@command('upgrade', owner=True, private=True)
def upgrade(phenny, msg):
    """Request remote upgrade using a cryptographic signature"""
    if ' ' not in msg.command_args:
        return
    pieces = msg.command_args.split()
    commit, signature = pieces[0], pieces[1]

    # check if we have a cryptographic public key

    if not os.path.isfile(os.path.expanduser('~/.phenny/id_rsa.pub')):
        phenny.reply('This instance has no cryptographic public key.')
        return

    # limit input space

    if not re.fullmatch('[0-9a-f]{40}', commit):
        phenny.reply('Invalid format: commit hash')
        return

    if not re.fullmatch('[A-Za-z0-9+/=]{172}', signature):
        phenny.reply('Invalid format: signature')
        return

    # check cryptographic signature

    if not check_signature(['.upgrade', commit], signature):
        phenny.reply('Signature is invalid')
        return

    phenny.reply('Signature is valid')
    os.system('git fetch --all')

    # ensure signature is not used twice

    current = get_output(['git', 'rev-parse', 'HEAD'])
    history = get_output(['git', 'rev-list', commit])

    if current not in history:
        phenny.reply('Specified commit must be newer than current.')
        return

    # deal with potentially dirty workspace

    if not check_return(['git', 'rebase', '--autostash', commit]):
        phenny.reply('Failed to rebase & autostash changes')
        return

    reload.restart(phenny)

@command('join', admin=True, private=True, priority='low', example='.join #example or .join #example key')
def join(phenny, msg):
    """Join the specified channel. This is an admin-only command."""
    channel, key = msg.command_args, None
    if ' ' in channel:
        channel, key = channel.split(' ', 1)
        key = key.lstrip()
    phenny.join(channel, key)

@event('INVITE', admin=True)
def autojoin(phenny, msg):
    """Join the specified channel when invited by an admin."""
    phenny.join(msg.text)

@command('part', admin=True, private=True, priority='low', example='.part #example')
def part(phenny, msg):
    """Part the specified channel. This is an admin-only command."""
    if msg.command_args.startswith('#'):
        phenny.part(msg.command_args)

@command('quit', owner=True, private=True, priority='low')
def quit(phenny, msg):
    phenny.quit()
    os.exit(0)

@command('msg', admin=True, private=True, priority='low')
def msg(phenny, msg):
    if ' ' not in msg.text:
        return
    channel, text = msg.command_args.split(' ', 1)
    phenny.msg(channel, text)

@command('me', admin=True, private=True, priority='low')
def me(phenny, msg):
    if ' ' not in msg.text:
        return
    channel, action = msg.command_args.split(' ', 1)
    phenny.msg(channel, '\x01ACTION %s\x01' % action)

if __name__ == '__main__':
    print(__doc__.strip())
