import html
import json
import re
import web
from web import ServerFault
from requests.exceptions import ContentDecodingError
from json.decoder import JSONDecodeError


r_tr = re.compile(r'(?ims)<tr[^>]*>.*?</tr>')
r_paragraph = re.compile(r'(?ims)<p[^>]*>.*?</p>|<li(?!n)[^>]*>.*?</li>')
r_tag = re.compile(r'<(?!!)[^>]+>')
r_whitespace = re.compile(r'[\t\r\n ]+')
r_redirect = re.compile(
    r'(?ims)class=.redirectText.>\s*<a\s*href=./wiki/([^"/]+)'
)

abbrs = ['etc', 'ca', 'cf', 'Co', 'Ltd', 'Inc', 'Mt', 'Mr', 'Mrs', 
         'Dr', 'Ms', 'Rev', 'Fr', 'St', 'Sgt', 'pron', 'approx', 'lit', 
         'syn', 'transl', 'sess', 'fl', 'Op', 'Dec', 'Brig', 'Gen'] \
   + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') \
   + list('abcdefghijklmnopqrstuvwxyz')
t_sentence = r'^.{5,}?(?<!\b%s)(?:\.(?=[\[ ][A-Z0-9]|\Z)|\Z)'
r_sentence = re.compile(t_sentence % r')(?<!\b'.join(abbrs))


def clean_text(dirty):
    dirty = r_tag.sub('', dirty)
    dirty = r_whitespace.sub(' ', dirty)
    return html.unescape(dirty).strip()

class Wiki(object):

    def __init__(self, api, url, searchurl=""):
        self.api = api
        self.url = url
        self.searchurl = searchurl

    def search(self, term, last=False):
        url = self.api.format(term)
        bytes = web.get(url)

        try:
            result = json.loads(bytes)
        except JSONDecodeError as e:
            raise ContentDecodingError(str(e))

        if 'error' in result:
            raise ServerFault(result['error'])

        result = result['query']['search']

        if not result:
            return None

        result = result[0]
        term = result['title']
        term = term.replace(' ', '_')
        snippet = clean_text(result['snippet'])
        return "{0}|{1}".format(snippet, self.url.format(term))
