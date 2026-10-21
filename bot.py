#!/usr/bin/env python3
"""
bot.py - Phenny IRC Bot
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import asyncio
import importlib
import logging
import os
import re
import sys
import threading
import time
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

class Origin(object):
    source = re.compile(r'([^!]*)!?([^@]*)@?(.*)')

    def __init__(self, bot, source, args):
        if not source:
            source = ""
        match = Origin.source.match(source)
        self.nick, self.user, self.host = match.groups()

        if len(args) > 1:
            target = args[1]
        else: target = None

        mappings = {bot.nick: self.nick, None: None}
        self.sender = mappings.get(target, target)

class Phenny:
    def __init__(self, config):
        self.config = config
        self.doc = {}
        self.stats = {}
        self.nick = config.nick
        self.channels = config.channels or []
        self.setup()
        self.sending = threading.RLock()
        self.stack = []

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

    def run(self, host, port=6667, ssl=False, ipv6=False, ca_certs=None,
            ssl_context=None):
        asyncio.run(self.main_loop(host, port, ssl))

    def write(self, args, text=None):
        def safe(arg):
            if isinstance(arg, str):
                arg = arg.encode('utf-8')
            return re.sub(b' ?[\r\n]+', b' ', arg)
        line = b' '.join([safe(arg) for arg in args])
        if text:
            line += b' :' + safe(text)
        self.sending.acquire()
        print('OUT:', line)
        self.writer.write(line + b'\r\n')
        self.sending.release()

    def msg(self, recipient, text, target=None):
        if target:
            text = target + ': ' + text

        # Cf. http://swhack.com/logs/2006-03-01#T19-43-25
        if isinstance(text, str):
            try: text = text.encode('utf-8')
            except UnicodeEncodeError as error:
                logger.error(str(error))
                text = error.__class__ + ': ' + str(error)
        if isinstance(recipient, str):
            try: recipient = recipient.encode('utf-8')
            except UnicodeEncodeError as error:
                logger.error(str(error))
                return

        # Split long messages
        if len(text) > tools.max_message_length:
            for message in tools.break_up(text, max_count=3):
                self.msg(recipient, message)
            return

        # No messages within the last 3 seconds? Go ahead!
        # Otherwise, wait so it's been at least 0.8 seconds + penalty
        if self.stack:
            elapsed = time.time() - self.stack[-1][0]
            if elapsed < 3:
                penalty = float(max(0, len(text) - 50)) / 70
                wait = 0.8 + penalty
                if elapsed < wait:
                    time.sleep(wait - elapsed)

        # Loop detection
        messages = [m[1:3] for m in self.stack[-10:]]
        if messages.count((recipient, text)) >= 3:
            text = '...'
            if messages.count((recipient, text)) >= 3:
                self.sending.release()
                return

        self.write(('PRIVMSG', recipient), text)
        self.stack.append((time.time(), recipient, text))
        self.stack = self.stack[-10:]

    def handle_line(self, line):
        print('IN:', line)
        try:
            line = line.decode('utf-8')
        except UnicodeDecodeError:
            line = line.decode('iso-8859-1')

        if line.startswith(':'):
            source, line = line[1:].split(' ', 1)
        else:
            source = None

        if ' :' in line:
            middle, trailing = line.split(' :', 1)
            middle = middle.split()
            args = tuple(middle + [trailing])
            text = trailing
        else:
            middle, trailing = line.split(), None
            args = tuple(middle)
            text = ''

        origin = Origin(self, source, args)
        print(f'\t{origin.nick=}, {origin.user=}, {origin.host=}, {origin.sender=}, {args=}, {text=}')
        self.dispatch(origin, args, text.rstrip())

        if args[0] == 'PING':
            self.write(('PONG', args[-1]))

    def error(self, report):
        logger.error(str(traceback.format_exc()))

    async def main_loop(self, host, port, ssl):
        self.reader, self.writer = await asyncio.open_connection(
            host, port, ssl=ssl)

        self.write(('NICK', self.config.nick))
        self.write(('USER', self.config.nick, '+iw', self.config.name))
        if hasattr(self.config, 'password'):
            self.write(('PRIVMSG', 'NickServ'),
                       'IDENTIFY %s' % self.config.password)
        for channel in self.config.channels:
            self.write(('JOIN', channel))

        while True:
            line = await self.reader.readline()
            if not line:
                break
            self.handle_line(line)

        self.writer.close()
        await self.writer.wait_closed()
        logger.info('Closed!')

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
            keys.append('(?!.*(?:->|→))' + regexp + '()')
            keys.append(regexp + r'\s(?:->|→)\s(\S*)')
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
        def report(*lines, verbose=True):
            for admin in self.config.admins:
                if verbose:
                    self.msg(admin, "Error in '{}/{}' with input '{}'"
                                    .format(func.__module__, func.__name__, input.bytes))
                for line in lines:
                    self.msg(admin, line)

        try:
            rephrase_errors(func, phenny, input)
        except GrumbleError as e:
            report(str(e), verbose=False)
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

    def join(self, channels, keys=None):
        if isinstance(channels, list):
            self.join(','.join(channels), keys)
            return
        if keys:
            if isinstance(keys, list):
                self.join(channels, ','.join(keys))
                return
            self.write(('JOIN', channels, keys))
        else:
            self.write(('JOIN', channels))

    def nick(self, nickname):
        self.write(('NICK', nickname))

    def notice(self, msgtarget, message):
        self.write(('NOTICE', msgtarget), message)

    def part(self, channels, message=None):
        if isinstance(channels, list):
            self.part(','.join(channels), keys)
            return
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

if __name__ == '__main__':
    print(__doc__)
