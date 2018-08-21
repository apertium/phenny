#!/usr/bin/env python3
"""
bot.py - Phenny IRC Bot
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import importlib
import irc
import logging
import os
import re
import sys
import threading
import traceback
import tools
from tools import GrumbleError, decorate, rephrase_errors

logger = logging.getLogger('phenny')

home = os.getcwd()

def decode(bytes): 
    if type(bytes) == str:
        return bytes
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError: 
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError: 
            text = bytes.decode('cp1252')
    except AttributeError:
        return bytes
    return text

def module_control(phenny, module, func):
    if not hasattr(module, func):
        return True

    try:
        rephrase_errors(getattr(module, func), phenny)
        return True
    except GrumbleError as e:
        desc = str(e)
    except Exception as e:
        desc = traceback.format_exc()

    name = os.path.basename(module.__file__)
    logger.error("Error during %s of %s module:\n%s" % (func, name, desc))
    return False

class Phenny(irc.Bot): 
    def __init__(self, config): 
        args = (config.nick, config.name, config.channels, config.password)
        irc.Bot.__init__(self, *args)
        self.config = config
        self.doc = {}
        self.stats = {}
        self.setup()

    def setup(self): 
        self.variables = {}

        filenames = []
        if not hasattr(self.config, 'enable'): 
            for fn in os.listdir(os.path.join(home, 'modules')): 
                if fn.endswith('.py') and not fn.startswith('_'): 
                    filenames.append(os.path.join(home, 'modules', fn))
        else: 
            for fn in self.config.enable: 
                filenames.append(os.path.join(home, 'modules', fn + '.py'))

        if hasattr(self.config, 'extra'): 
            for fn in self.config.extra: 
                if os.path.isfile(fn): 
                    filenames.append(fn)
                elif os.path.isdir(fn): 
                    for n in os.listdir(fn): 
                        if n.endswith('.py') and not n.startswith('_'): 
                            filenames.append(os.path.join(fn, n))

        tools.setup(self)

        modules = {}
        excluded_modules = getattr(self.config, 'exclude', [])

        for filename in filenames: 
            name = os.path.basename(filename)[:-3]
            if name in excluded_modules: continue

            try:
                module_loader = importlib.machinery.SourceFileLoader(name, filename)
                module = module_loader.load_module()
            except Exception as e: 
                trace = traceback.format_exc()
                logger.error("Error loading %s module:\n%s" % (name, trace))
                continue

            if module_control(self, module, 'setup'):
                self.register(module)
                modules[name] = module

        self.modules = modules

        if modules: 
            logger.info('Registered modules: ' + ', '.join(sorted(modules.keys())))
        else:
            logger.warning("Couldn't find any modules")

        self.bind_commands()

    def register(self, module):
        # This is used by reload.py, hence it being methodised
        if module.__name__ not in self.variables:
            self.variables[module.__name__] = {}

        for name, obj in vars(module).items():
            if hasattr(obj, 'commands') or hasattr(obj, 'rule'): 
                self.variables[module.__name__][name] = obj

    def bind(self, module, name, func, regexp):
        # register documentation
        if not hasattr(func, 'name'):
            func.name = func.__name__

        if func.__doc__:
            if hasattr(func, 'example'):
                example = func.example
                example = example.replace('$nickname', self.nick)
            else: example = None

            self.doc[func.name] = (func.__doc__, example)

        commands = self.commands[func.priority]
        keys = []

        if func.point:
            keys.append(regexp + '()')
            keys.append(regexp + '\s(?:->|→)\s(\S*)')
        else:
            keys.append(regexp)

        for key in keys:
            key = re.compile(key)
            commands.setdefault(key, []).append(func)

    def bind_command(self, module, name, func):
        logger.debug("Binding module '{:}' command '{:}'".format(module, name))

        defaults = {
            'priority': 'medium',
            'thread': True,
            'point': False,
            'event': 'PRIVMSG',
        }

        for key, value in defaults.items():
            if not hasattr(func, key):
                setattr(func, key, value)

        func.event = func.event.upper()

        def sub(pattern, self=self): 
            # These replacements have significant order
            pattern = pattern.replace('$nickname', re.escape(self.nick))
            return pattern.replace('$nick', r'%s[,:] +' % re.escape(self.nick))

        if hasattr(func, 'rule'):
            if isinstance(func.rule, str):
                pattern = sub(func.rule)
                regexp = pattern
                self.bind(module, name, func, regexp)

            if isinstance(func.rule, tuple):
                # 1) e.g. ('$nick', '(.*)')
                if len(func.rule) == 2 and isinstance(func.rule[0], str):
                    prefix, pattern = func.rule
                    prefix = sub(prefix)
                    regexp = prefix + pattern
                    self.bind(module, name, func, regexp)

                # 2) e.g. (['p', 'q'], '(.*)')
                elif len(func.rule) == 2 and isinstance(func.rule[0], list):
                    prefix = self.config.prefix
                    commands, pattern = func.rule
                    command = r'(?:%s)(?: +(%s))?' % ('|'.join(commands), pattern)
                    regexp = prefix + command
                    self.bind(module, name, func, regexp)

                # 3) e.g. ('$nick', ['p', 'q'], '(.*)')
                elif len(func.rule) == 3:
                    prefix, commands, pattern = func.rule
                    prefix = sub(prefix)
                    command = r'(?:%s) +' % '|'.join(commands)
                    regexp = prefix + command + pattern
                    self.bind(module, name, func, regexp)

        if hasattr(func, 'commands'):
            template = r'(?:%s)(?: +(.+))?'
            pattern = template % '|'.join(func.commands)
            regexp = self.config.prefix + pattern
            self.bind(module, name, func, regexp)

    def bind_commands(self):
        self.commands = {'high': {}, 'medium': {}, 'low': {}}

        for module, functions in self.variables.items():
            for name, func in functions.items():
                self.bind_command(module, name, func)

    def wrapped(self, origin, text, match):
        sender = origin.sender or text
        delegate = {
            'reply': lambda msg, target=origin.nick: self.msg(sender, msg, target=target),
            'say': lambda msg, target=None: self.msg(sender, msg, target=target),
            'do': lambda msg: self.action(sender, msg),
        }

        return decorate(self, delegate)

    def input(self, origin, text, match, args):
        class CommandInput(str): 
            def __new__(cls, text, origin,  match, args):
                s = str.__new__(cls, text)
                s.sender = decode(origin.sender)
                s.nick = decode(origin.nick)
                s.bytes = text
                s.group = match.group
                s.groups = match.groups
                s.args = args
                s.owner = s.nick == self.config.owner
                s.admin = (s.nick in self.config.admins) or s.owner
                return s

        return CommandInput(text, origin, match, args)

    def call(self, func, origin, phenny, input):
        def report(text):
            for admin in self.config.admins:
                self.msg(admin, text)

        try:
            rephrase_errors(func, phenny, input)
        except GrumbleError as e:
            report(str(e))
        except Exception as e: 
            self.error(report)

    def limit(self, origin, func): 
        if origin.sender and origin.sender.startswith('#'): 
            if hasattr(self.config, 'limit'): 
                limits = self.config.limit.get(origin.sender)
                if limits and (func.__module__ not in limits): 
                    return True
        return False

    def dispatch(self, origin, args, text):
        event = args[0]

        if origin.nick in self.config.ignore:
             return

        for priority in ('high', 'medium', 'low'): 
            items = list(self.commands[priority].items())

            for regexp, funcs in items: 
                for func in funcs: 
                    if event != func.event and func.event != '*': continue

                    match = regexp.fullmatch(text)
                    if not match: continue

                    if self.limit(origin, func): continue

                    phenny = self.wrapped(origin, text, match)
                    input = self.input(origin, text, match, args)

                    if func.thread:
                        targs = (func, origin, phenny, input)
                        t = threading.Thread(target=self.call, args=targs, name=func.name)
                        t.start()
                    else:
                        self.call(func, origin, phenny, input)

                    for source in [decode(origin.sender), decode(origin.nick)]:
                        try:
                            self.stats[(func.name, source)] += 1
                        except KeyError:
                            self.stats[(func.name, source)] = 1

if __name__ == '__main__': 
    print(__doc__)
