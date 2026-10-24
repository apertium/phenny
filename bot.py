#!/usr/bin/env python3
"""
bot.py - Phenny IRC Bot
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import asyncio
import collections
import dataclasses
import functools
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

@dataclasses.dataclass
class Message:
    line: str
    source: str = ''
    body: str = ''
    nick: str = ''
    user: str = ''
    host: str = ''
    text: str = ''
    args: tuple = ()
    sender: str = ''
    command: str = ''
    sub_command: str = ''
    command_args: str = ''
    command_point: str = ''
    command_args_list: list = None

    source_pattern = re.compile(r'([^!]*)!?([^@]*)@?(.*)')

    def __post_init__(self):
        if self.line.startswith(':'):
            self.source, self.body = self.line[1:].split(' ', 1)
            m = self.source_pattern.match(self.source)
            self.nick, self.user, self.host = m.groups()
        else:
            self.body = self.line
        if ' :' in self.body:
            self.body, self.text = self.body.split(' :', 1)
            self.text = self.text.rstrip()
        self.args = tuple(self.body.split())
        if len(self.args) > 1:
            self.sender = self.args[1]

COMMANDS = {}
KEYWORDS = []
EVENTS = collections.defaultdict(list)

def return_msg(ping=True):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(bot, msg):
            val = fn(bot, msg)
            if val:
                target = msg.command_point or msg.nick
                if not ping or not target:
                    target = None
                bot.msg(msg.sender, val, target=target)
        return wrapper
    return decorator

def command(commands, admin=False, owner=False, private=False, ping=True,
            priority='medium', example=None, thread=False):
    def decorator(fn):
        @functools.wraps(fn)
        @return_msg(ping=ping)
        def wrapper(bot, msg):
            if private and msg.sender.startswith('#'):
                return
            if owner and msg.nick != bot.config.owner:
                return
            if admin and msg.nick not in bot.config.admins and msg.nick != bot.config.owner:
                return
            return fn(bot, msg)
        global COMMANDS
        cmd = [commands] if isinstance(commands, str) else commands
        for c in cmd:
            COMMANDS[c] = wrapper
        if example:
            wrapper.example = example
        if thread:
            wrapper.thread = True
        return wrapper
    return decorator

def keyword(pattern, ping=True, priority='medium'):
    def decorator(fn):
        @functools.wraps(fn)
        @return_msg(ping=ping)
        def wrapper(bot, msg):
            return fn(bot, msg)
        global KEYWORDS
        pat = pattern
        if isinstance(pattern, str):
            pat = re.compile(pat)
        KEYWORDS.append((pat, wrapper))
        return wrapper
    return decorator

def event(etype, admin=False, thread=False):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(bot, msg):
            if admin and msg.nick not in bot.config.admins and msg.nick != bot.config.owner:
                return
            return fn(bot, msg)
        global EVENTS
        evt = [etype] if isinstance(etype, str) else etype
        for e in evt:
            EVENTS[e].append(wrapper)
        if thread:
            wrapper.thread = True
        return wrapper
    return decorator

def every_message(fn):
    @functools.wraps(fn)
    @event('*')
    def wrapper(bot, msg):
        if 'PRIVMSG' not in msg.args:
            return
        fn(bot, msg)
    return wrapper

class Phenny:
    def __init__(self, config):
        self.config = config
        self.doc = {}
        self.stats = collections.Counter()
        self.nick = config.nick
        self.channels = config.channels or []
        self.setup()
        self.sending = threading.RLock()
        self.stack = []
        np = re.escape(self.nick.lower())
        self.command_pattern = re.compile(r'(?i)^(?:'+np+r':\s+|\.|(?P<point1>\w+)[:,]\s+\.)(?P<cmd>\w+)(?:\.(?P<subcmd>\w+))?\s*(?P<args>.*)(?:\s*(?:->|→)\s*(?P<point2>\w+))?$')

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
                spec = importlib.util.spec_from_file_location(name, filename)
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
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

    def run(self, host, port=6667, ssl=False, ipv6=False, ca_certs=None,
            ssl_context=None):
        asyncio.run(self.main_loop(host, port, ssl))

    def prepare_outgoing_message(self, args, text=None):
        def safe(arg):
            if isinstance(arg, str):
                arg = arg.encode('utf-8')
            return re.sub(b' ?[\r\n]+', b' ', arg)
        line = b' '.join([safe(arg) for arg in args])
        if text:
            line += b' :' + safe(text)
        return line

    def write(self, args, text=None):
        line = self.prepare_outgoing_message(args, text)
        self.sending.acquire()
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
        try:
            line = line.decode('utf-8')
        except UnicodeDecodeError:
            line = line.decode('iso-8859-1')

        msg = Message(line)
        self.dispatch(msg)

        if msg.args[0] == 'PING':
            self.write(('PONG', msg.args[-1]))

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

    def wrapped(self, message):
        sender = message.sender or message.text
        if sender == self.nick:
            sender = message.nick
        delegate = {
            'reply': lambda msg, target=message.nick: self.msg(sender, msg, target=target),
            'say': lambda msg, target=None: self.msg(sender, msg, target=target),
            'do': lambda msg: self.action(sender, msg),
        }

        return decorate(self, delegate)

    def call(self, func, msg):
        if msg.sender.startswith('#') and hasattr(self.config, 'limit'):
            limits = self.config.limit.get(msg.sender)
            if limits and func.__module__ not in limits:
                return
        if hasattr(func, 'thread') and func.thread:
            t = threading.Thread(target=self.call_unthreaded,
                                 args=(func, msg), name=func.__name__)
            t.start()
        else:
            self.call_unthreaded(func, msg)
        self.stats[(func.__name__, msg.sender)] += 1
        self.stats[(func.__name__, msg.nick)] += 1

    def call_unthreaded(self, func, msg):
        phenny = self.wrapped(msg)
        def report(*lines, verbose=True):
            for admin in self.config.admins:
                if verbose:
                    self.msg(admin, "Error in '{}/{}' with input '{}'"
                                    .format(func.__module__, func.__name__, input.bytes))
                for line in lines:
                    self.msg(admin, line)

        try:
            rephrase_errors(func, phenny, msg)
        except GrumbleError as e:
            report(str(e), verbose=False)
        except Exception as e:
            self.error(report)

    def dispatch(self, msg):
        if msg.nick in self.config.ignore:
            return
        for fn in EVENTS['*']:
            self.call(fn, msg)
        if msg.args and msg.args[0] in EVENTS:
            for fn in EVENTS[msg.args[0]]:
                self.call(fn, msg)
        if msg.args and msg.args[0] != 'PRIVMSG':
            return
        m = self.command_pattern.fullmatch(msg.text)
        if m:
            cmd = m.group('cmd').lower()
            if cmd in COMMANDS:
                msg.command = cmd
                msg.sub_command = m.group('subcmd')
                msg.command_args = m.group('args')
                msg.command_args_list = msg.command_args.split()
                msg.command_point = m.group('point1') or m.group('point2') or None
                self.call(COMMANDS[cmd], msg)
                return
        for pat, fn in KEYWORDS:
            if pat.fullmatch(msg.text):
                self.call(fn, msg)

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

    def action(self, recipient, text):
        text = "\x01ACTION {0}\x01".format(text)
        return self.msg(recipient, text)

    def is_admin(self, nick):
        return nick in self.config.admins or nick == self.config.owner

if __name__ == '__main__':
    print(__doc__)
