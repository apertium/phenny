import html
import json
import lxml.html
import re
from requests.exceptions import ContentDecodingError
from urllib.parse import quote, unquote

from tools import truncate
import web
from web import ServerFault


r_tag = re.compile(r'<(?!!)[^>]+>')
r_whitespace = re.compile(r'[\t\r\n ]+')


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

def extract_snippet(url, origsection=None):
    page = lxml.html.fromstring(web.get(url))
    article = page.get_element_by_id('mw-content-text')

    if origsection:
        section = format_section(origsection)
        text = article.find(".//span[@id='%s']" % section)
        url += "#" + unquote(section)

        if text is None:
            return ("No '%s' section found." % origsection, url)

        text = text.getparent().getnext()
        content_tags = ['p', 'ul', 'ol']

        # div tag may come before the text
        while text.tag not in content_tags:
            text = text.getnext()
    else:
        text = article.find('./p')

        if text is None:
            text = article.find('./div/p')

    sentences = [x.strip() for x in text.text_content().split(".")]
    return (sentences[0], url)

class Wiki(object):

    def __init__(self, api, url, searchurl=""):
        self.api = api
        self.url = url
        self.searchurl = searchurl

    def search(self, term):
        term = deformat_term(term)
        term = quote(term)
        url = self.api.format(term)

        try:
            result = json.loads(web.get(url))
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
        return self.url.format(term)
