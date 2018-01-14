#!/usr/bin/env python3
"""
web.py - Web Facilities
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import re
import urllib.parse
import requests
import json as jsonlib
import lxml.html as lhtml
import unittest
import inspect
from time import time
from requests.exceptions import ConnectionError, HTTPError, InvalidURL, ReadTimeout
from html.entities import name2codepoint
from urllib.parse import quote, unquote


REQUEST_TIMEOUT = 10 # seconds
user_agent = "Mozilla/5.0 (Phenny)"
default_headers = {'User-Agent': user_agent}

up_down = {}

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
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            up_down[url] = (False, time())
    return up_down[url][0]

def catch_timeout(fn):
    def wrapper(*args, **kw):
        try:
            return fn(*args, **kw)
        except ReadTimeout:
            raise unittest.SkipTest("The server did not send any data in the allowed amount of time. Skipping test.")

    wrapper.__name__ = fn.__name__
    return wrapper

def catch_timeouts(cls):
    for name, method in inspect.getmembers(cls, inspect.ismethod):
        setattr(cls, name, catch_timeout(method))

    return cls

def get(uri, headers={}, verify=True, timeout=REQUEST_TIMEOUT, **kwargs):
    if not uri.startswith('http'): 
        return
    headers.update(default_headers)
    r = requests.get(uri, headers=headers, verify=verify, timeout=timeout, **kwargs)
    r.raise_for_status()
    # Fix charset if necessary
    if 'Content-Type' in r.headers:
        content_type = r.headers['Content-Type']
        if 'text/html' in content_type and 'charset' not in content_type:
            doc = lhtml.document_fromstring(r.text)
            head = doc.find("head")
            metas = head.findall("meta")
            for meta in metas:
                http_equiv = meta.get("http-equiv")
                if http_equiv != None and http_equiv.lower() == "content-type":
                    contents = [x.strip() for x in meta.get("content").split(";")]
                    for content in contents:
                        splitted = content.split("=")
                        if splitted[0] != None and splitted[0].lower() == "charset":
                            r.encoding = splitted[1]
                            return r.text
                if meta.get("charset"):
                    r.encoding = meta.get("charset")
                    return r.text
    return r.text

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

r_string = re.compile(r'("(\\.|[^"\\])*")')
r_json = re.compile(r'^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]+$')
env = {'__builtins__': None, 'null': None, 'true': True, 'false': False}

def json(text): 
    """Evaluate JSON text safely (we hope)."""
    return jsonlib.loads(text)

if __name__=="__main__": 
    main()
