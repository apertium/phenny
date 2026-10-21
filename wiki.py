import html
import json
import lxml.html
import re
from requests.exceptions import ContentDecodingError, HTTPError
from urllib.parse import quote, unquote

from tools import truncate
import web
from web import ServerFault


abbrs = [
    'etc', 'ca', 'cf', 'Co', 'Ltd', 'Inc', 'Mt', 'Mr', 'Mrs',
    'Dr', 'Ms', 'Rev', 'Fr', 'St', 'Sgt', 'pron', 'approx', 'lit',
    'syn', 'transl', 'sess', 'fl', 'Op', 'Dec', 'Brig', 'Gen',
] + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + list('abcdefghijklmnopqrstuvwxyz')
no_abbr = ''.join('(?<! ' + abbr + ')' for abbr in abbrs)
breaks = re.compile('(%s)+' % '|'.join([
    no_abbr + '[.!?](?:[ \n]|\\[[0-9]+\\]|$)',
    '。', '｡', '．', '！', '？',
]))


def format_term(term):
    term = term.replace(' ', '_')
    term = term[0].upper() + term[1:]
    return term

def deformat_term(term):
    term = term.replace('_', ' ')
    return term

def format_section(section):
    section = section.replace(' ', '_')
    section = quote(section)
    section = section.replace('%', '.')
    section = section.replace(".3A", ":")
    return section

def parse_term(origterm):
    if "#" in origterm:
        term, section = origterm.split("#")[:2]
        term, section = term.strip(), section.strip()
    else:
        term = origterm.strip()
        section = None

    return (term, section)

def good_content(text, content):
    if not content.strip():
        return False

    if not breaks.search(content):
        return False

    if text.tag not in ['p', 'ul', 'ol']:
        return False

    if text.find(".//span[@id='coordinates']") is not None:
        return False

    return True

def search_content(text):
    if text is None:
        return ""

    content = text.text_content()

    while not good_content(text, content):
        text = text.getnext()

        if text is None:
            return ""

        try:
            content = text.text_content()
        except ValueError:
            # HtmlComment causes weird errors
            content = ""

    return content

def extract_snippet(match, origsection=None):
    html, url = match
    page = lxml.html.fromstring(html)
    article = page.get_element_by_id('mw-content-text')

    if origsection:
        section = format_section(origsection)
        text = article.find(".//span[@id='%s']" % section)
        url += "#" + unquote(section)

        if text is None:
            return ("No '%s' section found." % origsection, url)

        text = text.getparent().getnext()
        content = search_content(text)

        if not content:
            return ("No section text found.", url)
    else:
        text = article.find('./p')

        if text is None:
            text = article.find('./div/p')

        content = search_content(text)

        if not content:
            return ("No introduction text found.", url)

    sentences = [x.strip() for x in breaks.split(content)]
    return (sentences[0], url)

class Wiki(object):

    def __init__(self, endpoints, lang):
        if lang:
            self.endpoints = {}

            for key in endpoints:
                self.endpoints[key] = endpoints[key] % lang
        else:
            self.endpoints = endpoints

    def search(self, term):
        try:
            exactterm = format_term(term)
            exactterm = quote(exactterm)
            exacturl = self.endpoints['url'].format(exactterm)
            html = web.get(exacturl)
            return (html, exacturl)
        except HTTPError:
            pass

        term = deformat_term(term)
        term = quote(term)
        apiurl = self.endpoints['api'].format(term)

        try:
            result = json.loads(web.get(apiurl))
        except ValueError as e:
            raise ContentDecodingError(str(e))

        if 'error' in result:
            raise ServerFault(result['error'])

        result = result['query']['search']

        if not result:
            return None

        term = result[0]['title']
        term = format_term(term)
        term = quote(term)

        url = self.endpoints['url'].format(term)
        html = web.get(url)
        return (html, url)
