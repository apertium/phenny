#!/usr/bin/env python3
"""
tools.py - Phenny Tools
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import os
import re
import base64
import sqlite3
import logging
from requests.exceptions import ConnectionError, HTTPError, Timeout
import socket
import socketserver
import pickle
import inspect
from time import time

logger = logging.getLogger('phenny')


# maximum message length (see msg() in irc.py)
# overriden if max_message_length exists in the config
max_message_length = 430

dotdir = os.path.expanduser('~/.phenny')

def setup(self):
    global max_message_length

    if hasattr(self.config, 'max_message_length'):
        max_message_length = self.config.max_message_length

def urlsafe_encode(string):
    return base64.urlsafe_b64encode(string.encode('utf-8')).decode('ascii')

def dot_path(filename):
    path = os.path.join(dotdir, filename)
    dirname = os.path.dirname(path)
    os.makedirs(dirname, exist_ok=True)
    return path

def write_obj(path, data):
    with open(path, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

def read_obj(path, warn_after=None):
    try:
        last_changed = os.path.getmtime(path)
    except FileNotFoundError as e:
        raise GrumbleError() from e

    if warn_after and (time() - last_changed) > warn_after:
        raise ResourceWarning('Database out of date')

    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    # Pickling may throw anything
    except Exception as e:
        raise GrumbleError() from e

def db_path(self, name):
    return dot_path('%s-%s.%s.db' % (self.nick, self.config.host, name))

def write_db(self, name, data, **kwargs):
    write_obj(db_path(self, name), data, **kwargs)

def read_db(self, name, **kwargs):
    return read_obj(db_path(self, name), **kwargs)

def cache_path(name):
    return dot_path('cache/' + urlsafe_encode(name))

def write_cache(name, data):
    write_obj(cache_path(name), data)

def read_cache(name):
    path = cache_path(name)
    thirty_days = 30*24*60*60

    try:
        return read_obj(path, warn_after=thirty_days)
    except (GrumbleError, ResourceWarning):
        return None

class DatabaseCursor():
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.connection = sqlite3.connect(
            self.path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            isolation_level=None
        )
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, *args):
        self.cursor.close()
        self.connection.close()

class PortReuseTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

def encodeIfNot(text):
    if isinstance(text, str):
        try:
            return text.encode('utf-8')
        except UnicodeEncodeError as error:
            logger.error(str(error))
            return (error.__class__ + ': ' + str(error)).encode('utf-8')

    return text

def break_up(text, max_length=max_message_length, max_count=None):
    text = encodeIfNot(text)

    if len(text) <= max_length:
        return [text.decode('utf-8', 'ignore')]

    parts = []

    while len(text) > max_length:
        # We want to add "..." to last message so we leave place for it
        if max_count and len(parts) == max_count - 1:
            max_length -= 3

        space_index = text.rfind(b' ', 0, max_length)
        newline_index = text.rfind(b'\n', 0, max_length)
        offset = 0

        if space_index == -1 and newline_index == -1:
            msg_break = max_length
        elif space_index > newline_index:
            msg_break = space_index
            offset = 1
        else:
            msg_break = newline_index

        message = text[:msg_break]
        text = text[msg_break + offset:]

        # We want to add "..." to last message
        if max_count and len(parts) == max_count - 1:
            message += b'...'
            text = b''

        parts.append(message.decode('utf-8', 'ignore'))

    if text:
        parts.append(text.decode('utf-8', 'ignore'))

    return parts

def truncate(text, template=None, max_length=max_message_length):
    text = encodeIfNot(text)

    if template:
        max_length -= len(template.encode('utf-8')) - len(b'%s')

    if len(text) <= max_length:
        text = text.decode('utf-8', 'ignore')
    else:
        max_length -= 3

        space_index = text.rfind(b' ', 0, max_length)
        newline_index = text.rfind(b'\n', 0, max_length)

        if space_index == -1 and newline_index == -1:
            text = text[:max_length]
        elif space_index > newline_index:
            text = text[:space_index]
        else:
            text = text[:newline_index]

        text = text.decode('utf-8', 'ignore') + '...'

    if template:
        return template % text
    else:
        return text

def decorate(obj, delegate):
    class Decorator(object):
        def __getattr__(self, attr):
            if attr in delegate:
                return delegate[attr]

            return getattr(obj, attr)

        def __setattr__(self, attr, value):
            return setattr(obj, attr, value)

    return Decorator()

class GrumbleError(Exception):
    pass

def rephrase_errors(fn, *args, **kw):
    '''Simplfiy error messages for well-known exceptions'''

    try:
        return fn(*args, **kw)
    except ConnectionError as e:
        raise GrumbleError("Can't connect to %s" % e.request.url)
    except HTTPError as e:
        raise GrumbleError("HTTP protocol issue: %s" % str(e))
    except Timeout:
        raise GrumbleError("Network timed out")

def calling_module():
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0])
    return module.__name__

def generate_report(repo, author, comment, modified_paths, added_paths, removed_paths, rev, date=None):
    modified_paths = ['/' + x for x in modified_paths]
    added_paths = ['/' + x for x in added_paths]
    removed_paths = ['/' + x for x in removed_paths]

    paths = modified_paths + added_paths + removed_paths

    if not paths:
        return

    if comment is None:
        comment = "No commit message provided!"
    else:
        comment = re.sub("[\n\r]+", " ␍ ", comment.strip())

    basepath = os.path.commonprefix(paths)

    if basepath and basepath[-1] != '/':
        basepath = basepath.split('/')[:-1]
        basepath = '/'.join(basepath) + '/'

    text_paths = []

    for path in paths:
        addition = ''

        if path in added_paths:
            addition = " (+)"
        elif path in removed_paths:
            addition = " (-)"

        text_paths.append(os.path.relpath(path, basepath) + addition)

    if len(text_paths) > 1:
        if len(text_paths) <= 3:
            final_path = "%s: %s" % (basepath, ', '.join(text_paths))
        else:
            final_path = "%s: %s" % (basepath, ', '.join(text_paths[:2]) + " and %s other files" % str(len(text_paths) - 2))
    else:
        final_path = paths[0] + text_paths[0]

    msg = "%s: %s * %s: %s: %s" % (repo, author, rev, final_path, comment.strip())

    if date:
        msg = "[%s] %s" % (date, msg)

    return msg

if __name__ == '__main__': 
    print(__doc__.strip())
