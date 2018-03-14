#!/usr/bin/env python3
"""
proto.py - IRC protocol messages
"""

import sys
import traceback

def _comma(arg):
    if type(arg) is list:
        arg = ','.join(arg)
    return arg


def join(self, channels, keys=None):
    channels = _comma(channels)

    if keys:
        keys = _comma(keys)
        self.write(('JOIN', channels, keys))
    else:
        self.write(('JOIN', channels))

def nick(self, nickname):
    self.write(('NICK', nickname))

def notice(self, msgtarget, message):
    self.write(('NOTICE', msgtarget), message)

def part(self, channels, message=None):
    channels = _comma(channels)
    self.write(('PART', channels), message)

def pass_(self, password):
    self.write(('PASS', password))

def ping(self, server1, server2=None):
    self.write(('PING', server1), server2)

def pong(self, server1, server2=None):
    self.write(('PONG', server1), server2)

def privmsg(self, msgtarget, message):
    self.write(('PRIVMSG', msgtarget), message)

def quit(self, message=None):
    self.write(('QUIT'), message)

def user(self, user, mode, realname):
    self.write(('USER', user, mode, '_'), realname)


module_dict = sys.modules[__name__].__dict__
command_filter = lambda k, v: callable(v) and not k.startswith('_')
commands = {k: v for k, v in module_dict.items() if command_filter(k, v)}
