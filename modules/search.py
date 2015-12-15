#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web

def google_ajax(query): 
    """Search using AjaxSearch, and return its JSON."""
    if isinstance(query, str): 
        query = query.encode('utf-8')
    uri = 'http://ajax.googleapis.com/ajax/services/search/web'
    args = '?v=1.0&safe=off&q=' + web.quote(query)
    bytes = web.get(uri + args, headers={'Referer': 'https://github.com/sbp/phenny'})
    return web.json(bytes)

def google_search(query): 
    results = google_ajax(query)
    try: return results['responseData']['results'][0]['unescapedUrl']
    except IndexError: return None
    except TypeError: 
        print(results)
        return False

def google_count(query): 
    results = google_ajax(query)
    if 'responseData' not in results: return '0'
    if 'cursor' not in results['responseData']: return '0'
    if 'estimatedResultCount' not in results['responseData']['cursor']: 
        return '0'
    return results['responseData']['cursor']['estimatedResultCount']

def formatnumber(n): 
    """Format a number with beautiful commas."""
    parts = list(str(n))
    for i in range((len(parts) - 3), 0, -3):
        parts.insert(i, ',')
    return ''.join(parts)


def google_it(phenny, query, sender, to_user=None):
    uri = google_search(query)
    if uri: 
        if to_user:
            phenny.say(to_user+', '+uri)
        else:
            phenny.reply(uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[sender] = uri
    elif uri is False: phenny.reply("Problem getting data from Google.")
    else: phenny.reply("No results found for '%s'." % query)


def g(phenny, input): 
    """Queries Google for the specified input."""
    query = input.group(2)
    if not query: 
        return phenny.reply('.g what?')

    if "->" in query: return
    if "→" in query: return

    match_point_cmd = r'point\s(\S*)\s(.*)'
    matched_point = re.compile(match_point_cmd).match(query)
    if matched_point:
        to_nick = matched_point.groups()[0]
        query2 = matched_point.groups()[1]

        google_it(phenny, query2, input.sender, to_user=to_nick)
        return

    google_it(phenny, query, input.sender)

g.commands = ['g']
g.priority = 'high'
g.example = '.g swhack'


def g2(phenny, input):
    nick, _, __, query = input.groups()

    google_it(phenny, query, input.sender, to_user=nick)

g2.rule = r'(\S*)(:|,)\s\.(g)\s(.*)'
g2.example = 'svineet: .g extrapolate'


def g3(phenny, input):
    _, query, __, nick = input.groups()

    google_it(phenny, query, input.sender, to_user=nick)


g3.rule = r'\.(g)\s(.*)\s(->|→)\s(\S*)'
g3.example = '.g extrapolate -> svineet'


def gc(phenny, input): 
    """Returns the number of Google results for the specified input."""
    query = input.group(2)
    if not query: 
        return phenny.reply('.gc what?')
    num = formatnumber(google_count(query))
    phenny.say(query + ': ' + num)
gc.commands = ['gc']
gc.priority = 'high'
gc.example = '.gc extrapolate'

r_query = re.compile(
    r'\+?"[^"\\]*(?:\\.[^"\\]*)*"|\[[^]\\]*(?:\\.[^]\\]*)*\]|\S+'
)

def gcs(phenny, input): 
    """Compare the number of Google results for the specified paramters."""
    if not input.group(2):
        return phenny.reply("Nothing to compare.")
    queries = r_query.findall(input.group(2))
    if len(queries) > 6: 
        return phenny.reply('Sorry, can only compare up to six things.')

    results = []
    for i, query in enumerate(queries): 
        query = query.strip('[]')
        n = int((formatnumber(google_count(query)) or '0').replace(',', ''))
        results.append((n, query))
        if i >= 2: __import__('time').sleep(0.25)
        if i >= 4: __import__('time').sleep(0.25)

    results = [(term, n) for (n, term) in reversed(sorted(results))]
    reply = ', '.join('%s (%s)' % (t, formatnumber(n)) for (t, n) in results)
    phenny.say(reply)
gcs.commands = ['gcs', 'comp']
gcs.example = '.gcs Ronaldo Messi'

r_bing = re.compile(r'<h3><a href="([^"]+)"')

def bing_search(query, lang='en-GB'): 
    query = web.quote(query)
    base = 'http://www.bing.com/search?mkt=%s&q=' % lang
    bytes = web.get(base + query)
    m = r_bing.search(bytes)
    if m: return m.group(1)

def bing(phenny, input): 
    """Queries Bing for the specified input."""
    query = input.group(2)
    if query.startswith(':'): 
        lang, query = query.split(' ', 1)
        lang = lang[1:]
    else: lang = 'en-GB'
    if not query:
        return phenny.reply('.bing what?')

    uri = bing_search(query, lang)
    if uri: 
        phenny.reply(uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.reply("No results found for '%s'." % query)
bing.commands = ['bing']
bing.example = '.bing swhack'

r_duck = re.compile(r'nofollow" class="[^"]+" href="(http.*?)">')

def duck_search(query): 
    query = query.replace('!', '')
    query = web.quote(query)
    uri = 'http://duckduckgo.com/html/?q=%s&kl=uk-en' % query
    bytes = web.get(uri)
    m = r_duck.search(bytes)
    if m: return web.decode(m.group(1))

def duck(phenny, input): 
    """Queries DuckDuckGo for specified input."""
    query = input.group(2)
    if not query: return phenny.reply('.ddg what?')

    uri = duck_search(query)
    if uri: 
        phenny.reply(uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.reply("No results found for '%s'." % query)
duck.commands = ['duck', 'ddg']
duck.example = '.duck football'

def search(phenny, input): 
    if not input.group(2): 
        return phenny.reply('.search for what?')
    query = input.group(2)
    gu = google_search(query) or '-'
    bu = bing_search(query) or '-'
    du = duck_search(query) or '-'

    if (gu == bu) and (bu == du): 
        result = '%s (g, b, d)' % gu
    elif (gu == bu): 
        result = '%s (g, b), %s (d)' % (gu, du)
    elif (bu == du): 
        result = '%s (b, d), %s (g)' % (bu, gu)
    elif (gu == du): 
        result = '%s (g, d), %s (b)' % (gu, bu)
    else: 
        if len(gu) > 250: gu = '(extremely long link)'
        if len(bu) > 150: bu = '(extremely long link)'
        if len(du) > 150: du = '(extremely long link)'
        result = '%s (g), %s (b), %s (d)' % (gu, bu, du)

    phenny.reply(result)
search.commands = ['search']

def suggest(phenny, input): 
    if not input.group(2):
        return phenny.reply("No query term.")
    query = input.group(2)
    uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
    answer = web.get(uri + web.quote(query).replace('+', '%2B'))
    if answer: 
        phenny.say(answer)
    else: phenny.reply('Sorry, no result.')
suggest.commands = ['suggest']

def lmgtfy(phenny, input):
    if not input.group(2):
        phenny.reply('.lmgtfy what f who?')
    try:
        (who, what) = input.group(2).split(' ', 1)
        response = "%s: http://lmgtfy.com/?q=%s"
        what = web.quote(what)
        phenny.say(response % (who, what))
    except ValueError:
        phenny.reply('.lmgtfy what for who? (enter a nick and a query)')
lmgtfy.commands = ['lmgtfy']

if __name__ == '__main__': 
    print(__doc__.strip())
