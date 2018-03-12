#!/usr/bin/env python3
"""
web.py - Web Facilities
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import re
import urllib
import requests
import lxml.html as lhtml
import unittest
import inspect
import socket
from time import time
from requests.exceptions import ConnectionError, ContentDecodingError, HTTPError, Timeout
from html.entities import name2codepoint
from urllib.parse import quote, unquote
from tools import read_cache, write_cache


REQUEST_TIMEOUT = 10 # seconds
socket.setdefaulttimeout(REQUEST_TIMEOUT)

user_agent = "Mozilla/5.0 (Phenny)"
default_headers = {'User-Agent': user_agent}

up_down = {}

class ServerFault(Exception):
    def __init__(self, description):
        self.description = description
    def __str__(self):
        return str(self.description)

class Grab(urllib.request.URLopener): 
    def __init__(self, *args): 
        self.version = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17'
        urllib.request.URLopener.__init__(self, *args)
    def http_error_default(self, url, fp, errcode, errmsg, headers): 
        return urllib.addinfourl(fp, [headers, errcode], "http:" + url)
urllib.request._urlopener = Grab()

def is_up(url):
    global up_down

    if (url not in up_down) or (time() - up_down[url][1] > 600):
        try:
            requests.get(url, timeout=REQUEST_TIMEOUT).raise_for_status()
            up_down[url] = (True, time())
        except (HTTPError, ConnectionError, Timeout):
            up_down[url] = (False, time())
    return up_down[url][0]

def catch_timeout(fn):
    def wrapper(*args, **kw):
        try:
            return fn(*args, **kw)
        except (ConnectionError, ContentDecodingError, HTTPError, ServerFault, Timeout):
            raise unittest.SkipTest("The server is apparently down. Skipping test.")

    wrapper.__name__ = fn.__name__
    return wrapper

def get(url, cache=False, headers={}, verify=True, timeout=REQUEST_TIMEOUT, **kwargs):
    if not url.startswith('http'):
        return

    if cache:
        response = read_cache(url)
    else:
        response = None

    if not response:
        headers.update(default_headers)
        response = requests.get(url, headers=headers, verify=verify, timeout=timeout, **kwargs)
        response.raise_for_status()

    if cache:
        write_cache(url, response)

    # Fix charset if necessary
    if 'Content-Type' in response.headers:
        content_type = response.headers['Content-Type']
        if 'text/html' in content_type and 'charset' not in content_type:
            doc = lhtml.document_fromstring(response.text)
            head = doc.find("head")
            metas = head.findall("meta")
            for meta in metas:
                http_equiv = meta.get("http-equiv")
                if http_equiv != None and http_equiv.lower() == "content-type":
                    contents = [x.strip() for x in meta.get("content").split(";")]
                    for content in contents:
                        splitted = content.split("=")
                        if splitted[0] != None and splitted[0].lower() == "charset":
                            response.encoding = splitted[1]
                            return response.text
                if meta.get("charset"):
                    response.encoding = meta.get("charset")
                    return response.text
    return response.text

def get_page(domain, url, encoding='utf-8', port=80):
    conn = http.client.HTTPConnection(domain, port, timeout=REQUEST_TIMEOUT)
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    return res.read().decode(encoding)

def head(uri, headers={}, verify=True, **kwargs): 
    if not uri.startswith('http'): 
        return
    headers.update(default_headers)
    r = requests.head(uri, headers=headers, verify=verify, **kwargs)
    r.raise_for_status()
    return r.headers

def post(uri, data, headers={}, verify=True, **kwargs): 
    if not uri.startswith('http'): 
        return
    headers.update(default_headers)
    r = requests.post(uri, data=data, headers=headers, verify=verify, **kwargs)
    r.raise_for_status()
    return r.text

r_entity = re.compile(r'&([^;\s]+);')

def entity(match): 
    value = match.group(1).lower()
    if value.startswith('#x'): 
        return chr(int(value[2:], 16))
    elif value.startswith('#'): 
        return chr(int(value[1:]))
    elif value in name2codepoint: 
        return chr(name2codepoint[value])
    return '[' + value + ']'

def decode(html): 
    return r_entity.sub(entity, html)
