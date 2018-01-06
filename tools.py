#!/usr/bin/env python3
"""
tools.py - Phenny Tools
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import http.client
import os
import re
import urllib.request, urllib.parse, urllib.error
import json
import requests
import web
import itertools
import sqlite3
import logging
import socket
import socketserver
from time import time

logger = logging.getLogger('phenny')


headers = {
   'User-Agent': 'Mozilla/5.0' + '(X11; U; Linux i686)' + 'Gecko/20071127 Firefox/2.0.0.11'
}

# maximum message length (see msg() in irc.py)
# overriden if max_message_length exists in the config
max_message_length = 430

def setup(self):
    global max_message_length

    if hasattr(self.config, 'max_message_length'):
        max_message_length = self.config.max_message_length

def db_path(self, name):
    filename = self.nick + '-' + self.config.host + '.' + name + '.db'
    return os.path.join(os.path.expanduser('~/.phenny'), filename)

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

def truncate(text, share=None, max_length=max_message_length):
    text = encodeIfNot(text)

    if share:
        share = encodeIfNot(share)
        max_length -= len(share)

    if len(text) <= max_length:
        return text.decode('utf-8', 'ignore')

    max_length -= 3

    space_index = text.rfind(b' ', 0, max_length)
    newline_index = text.rfind(b'\n', 0, max_length)

    if space_index == -1 and newline_index == -1:
        return text[:max_length].decode('utf-8', 'ignore') + '...'
    elif space_index > newline_index:
        return text[:space_index].decode('utf-8', 'ignore') + '...'
    else:
        return text[:newline_index].decode('utf-8', 'ignore') + '...'

class GrumbleError(Exception):
    pass

def deprecated(old): 
    def new(phenny, input, old=old): 
        self = phenny
        origin = type('Origin', (object,), {
            'sender': input.sender, 
            'nick': input.nick
        })()
        match = input.match
        args = [input.bytes, input.sender, '@@']

        old(self, origin, match, args)
    new.__module__ = old.__module__
    new.__name__ = old.__name__
    return new

def generate_report(repo, author, comment, modified_paths, added_paths, removed_paths, rev, date=""):
    paths = modified_paths + added_paths + removed_paths

    if comment is None:
        comment = "No commit message provided!"
    else:
        comment = re.sub("[\n\r]+", " ␍ ", comment.strip())

    basepath = os.path.commonprefix(paths)

    if len(basepath) > 0:
        if basepath[-1] != "/":
            basepath = basepath.split("/")
            basepath.pop()
            basepath = '/'.join(basepath) + "/"

    text_paths = []
    if len(paths) > 0:
        for path in paths:
            addition = ""
            if path in added_paths:
                addition = " (+)"
            elif path in removed_paths:
                addition = " (-)"
            text_paths.append(os.path.relpath(path, basepath) + addition)
        if len(text_paths) > 1:
            if len(text_paths) <= 3: 
                final_path = "%s: %s" % (basepath, ', '.join(text_paths))
            else:
                final_path = "%s: %s" % (basepath, ', '.join([text_paths[0], text_paths[1]]) + ' and %s other files' % str(len(text_paths) - 2))
        else:
            final_path = paths[0]
            if final_path in added_paths:
                final_path += " (+)"
            elif final_path in removed_paths:
                final_path += " (-)"
            # if a file's modified, we don't want to say anything
            #else:
            #    final_path += " 0"
            # but we do want to set the string if it hasn't been set, I guess?
            else:
                final_path += ""
        # the following used to be outside the big if
        # but it would try to report revs with empty info
        # ... which we don't want
        if date == "":
            msg = "%s: %s * %s: %s: %s" % (repo, author, rev, final_path, comment.strip())
        else:
            msg = "[%s] %s: %s * %s: %s: %s" % (date, repo, author, rev, final_path, comment.strip())
        return msg
    #else: final_path = "empty"
    #if final_path is None: final_path = "empty"


def get_page(domain, url, encoding='utf-8', port=80): #get the HTML of a webpage.
    conn = http.client.HTTPConnection(domain, port, timeout=60)
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    return res.read().decode(encoding)

up_down = {}
def is_up(url):
    global up_down
    if (url not in up_down) or (time() - up_down[url][1] > 600):
        try:
            requests.get(url, timeout=4).raise_for_status()
            up_down[url] = (True, time())
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            up_down[url] = (False, time())
    return up_down[url][0]

def translate(phenny, translate_me, input_lang, output_lang='en'): 
    input_lang, output_lang = urllib.parse.quote(input_lang), urllib.parse.quote(output_lang)
    translate_me = urllib.parse.quote(translate_me)
    response = ""
    if hasattr(phenny.config, 'translate_url'):
        response = get_page(self.phenny.config.translate_url, '/translate?q=%s&langpair=%s|%s' % (translate_me, input_lang, output_lang))
    else:
        response = get_page('apy.projectjj.com', '/translate?q=%s&langpair=%s|%s' % (translate_me, input_lang, output_lang), port=2737)	

    responseArray = json.loads(response)
    if int(responseArray['responseStatus']) != 200:
        raise GrumbleError('APIerrorHttp' % (responseArray['responseStatus'], responseArray['responseDetails']))
    if responseArray['responseData']['translatedText'] == []:
        raise GrumbleError('APIerrorData')

    translated_text = responseArray['responseData']['translatedText']
    return translated_text

if __name__ == '__main__': 
    print(__doc__.strip())
