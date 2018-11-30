#!/usr/bin/env python3

# This script downloads specified language module to a given directory, compiles it,
# downloads the latest wikipedia archive for that language and runs
# coverage over it.

# Can be also used with docker, using additional parameter --docker

import os.path
import sys
import re
import gc
import bz2
import argparse
import urllib.request
import urllib.parse
import urllib.error
import subprocess
import logging
import time
import tempfile
import collections
import shutil
import mimetypes
from html.entities import name2codepoint

docker_script = '''FROM ubuntu:14.04
ADD autocoverage.py /
ADD apertium-{0} /apertium-{0}/
RUN apt-get update
RUN apt-get install -y software-properties-common python-software-properties
RUN apt-get install -y wget
RUN rm -rf /var/lib/apt/lists/*
RUN wget https://apertium.projectjj.com/apt/install-nightly.sh -O - | sudo bash
RUN wget https://apertium.projectjj.com/apt/install-release.sh -O - | sudo bash
RUN apt-get -f install -y apertium-all-dev
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV PYTHONIOENCODING=utf-8
RUN export LANG=C.UTF-8
CMD python3 autocoverage.py --lang {1} --is_docker_instance'''

ISO_639_3_TO_1 = {
    'aar': 'aa',
    'abk': 'ab',
    'ave': 'ae',
    'afr': 'af',
    'aka': 'ak',
    'amh': 'am',
    'arg': 'an',
    'ara': 'ar',
    'asm': 'as',
    'ava': 'av',
    'aym': 'ay',
    'aze': 'az',
    'bak': 'ba',
    'bel': 'be',
    'bul': 'bg',
    'bis': 'bi',
    'bam': 'bm',
    'ben': 'bn',
    'bod': 'bo',
    'bre': 'br',
    'bos': 'bs',
    'cat': 'ca',
    'che': 'ce',
    'cha': 'ch',
    'cos': 'co',
    'cre': 'cr',
    'ces': 'cs',
    'chu': 'cu',
    'chv': 'cv',
    'cym': 'cy',
    'dan': 'da',
    'deu': 'de',
    'div': 'dv',
    'dzo': 'dz',
    'ewe': 'ee',
    'ell': 'el',
    'eng': 'en',
    'epo': 'eo',
    'spa': 'es',
    'est': 'et',
    'eus': 'eu',
    'fas': 'fa',
    'ful': 'ff',
    'fin': 'fi',
    'fij': 'fj',
    'fao': 'fo',
    'fra': 'fr',
    'fry': 'fy',
    'gle': 'ga',
    'gla': 'gd',
    'glg': 'gl',
    'grn': 'gn',
    'guj': 'gu',
    'glv': 'gv',
    'hau': 'ha',
    'heb': 'he',
    'hin': 'hi',
    'hmo': 'ho',
    'hrv': 'hr',
    'hat': 'ht',
    'hun': 'hu',
    'hye': 'hy',
    'her': 'hz',
    'ina': 'ia',
    'ind': 'id',
    'ile': 'ie',
    'ibo': 'ig',
    'iii': 'ii',
    'ipk': 'ik',
    'ido': 'io',
    'isl': 'is',
    'ita': 'it',
    'iku': 'iu',
    'jpn': 'ja',
    'jav': 'jv',
    'kat': 'ka',
    'kon': 'kg',
    'kik': 'ki',
    'kua': 'kj',
    'kaz': 'kk',
    'kal': 'kl',
    'khm': 'km',
    'kan': 'kn',
    'kor': 'ko',
    'kau': 'kr',
    'kas': 'ks',
    'kur': 'ku',
    'kom': 'kv',
    'cor': 'kw',
    'kir': 'ky',
    'lat': 'la',
    'ltz': 'lb',
    'lug': 'lg',
    'lim': 'li',
    'lin': 'ln',
    'lao': 'lo',
    'lit': 'lt',
    'lub': 'lu',
    'lav': 'lv',
    'mlg': 'mg',
    'mah': 'mh',
    'mri': 'mi',
    'mkd': 'mk',
    'mal': 'ml',
    'mon': 'mn',
    'mar': 'mr',
    'msa': 'ms',
    'mlt': 'mt',
    'mya': 'my',
    'nau': 'na',
    'nob': 'nb',
    'nde': 'nd',
    'nep': 'ne',
    'ndo': 'ng',
    'nld': 'nl',
    'nno': 'nn',
    'nor': 'no',
    'nbl': 'nr',
    'nav': 'nv',
    'nya': 'ny',
    'oci': 'oc',
    'oji': 'oj',
    'orm': 'om',
    'ori': 'or',
    'oss': 'os',
    'pan': 'pa',
    'pli': 'pi',
    'pol': 'pl',
    'pus': 'ps',
    'por': 'pt',
    'que': 'qu',
    'roh': 'rm',
    'run': 'rn',
    'ron': 'ro',
    'rus': 'ru',
    'kin': 'rw',
    'san': 'sa',
    'srd': 'sc',
    'snd': 'sd',
    'sme': 'se',
    'sag': 'sg',
    'hbs': 'sh',
    'sin': 'si',
    'slk': 'sk',
    'slv': 'sl',
    'smo': 'sm',
    'sna': 'sn',
    'som': 'so',
    'sqi': 'sq',
    'srp': 'sr',
    'ssw': 'ss',
    'sot': 'st',
    'sun': 'su',
    'swe': 'sv',
    'swa': 'sw',
    'tam': 'ta',
    'tel': 'te',
    'tgk': 'tg',
    'tha': 'th',
    'tir': 'ti',
    'tuk': 'tk',
    'tgl': 'tl',
    'tsn': 'tn',
    'ton': 'to',
    'tur': 'tr',
    'tso': 'ts',
    'tat': 'tt',
    'twi': 'tw',
    'tah': 'ty',
    'uig': 'ug',
    'ukr': 'uk',
    'urd': 'ur',
    'uzb': 'uz',
    'ven': 've',
    'vie': 'vi',
    'vol': 'vo',
    'wln': 'wa',
    'wol': 'wo',
    'xho': 'xh',
    'yid': 'yi',
    'yor': 'yo',
    'zha': 'za',
    'zho': 'zh',
    'zul': 'zu'}

prefix = None

##
# Whether to preseve links in output
#
keepLinks = False

##
# Whether to transform sections into HTML
#
keepSections = False

##
# Recognize only these namespaces
# w: Internal links to the Wikipedia
#
acceptedNamespaces = set(['w'])

##
# Drop these elements from article text
#
discardElements = set([
    'gallery', 'timeline', 'noinclude', 'pre',
    'table', 'tr', 'td', 'th', 'caption',
    'form', 'input', 'select', 'option', 'textarea',
    'ul', 'li', 'ol', 'dl', 'dt', 'dd', 'menu', 'dir',
    'ref', 'references', 'img', 'imagemap', 'source'
])

def WikiDocumentSentences(out, id, title, tags, text):
    url = get_url(id, prefix)
    header = '\n{0}:{1}'.format(title, "|||".join(tags))
    # Separate header from text with a newline.
    text = clean(text)

    out.reserve(len(header) + len(text))
    print(header, file=out)
    for line in compact(text, structure=False):
        print(line, file=out)


def get_url(id, prefix):
    return "%s?curid=%s" % (prefix, id)

#------------------------------------------------------------------------------
# Modified WikiExtractor.py scirpt from:
# https://svn.code.sf.net/p/apertium/svn/trunk/apertium-tools/WikiExtractor.py


selfClosingTags = ['br', 'hr', 'nobr', 'ref', 'references']

# handle 'a' separetely, depending on keepLinks
ignoredTags = [
    'b', 'big', 'blockquote', 'center', 'cite', 'div', 'em',
    'font', 'h1', 'h2', 'h3', 'h4', 'hiero', 'i', 'kbd', 'nowiki',
    'p', 'plaintext', 's', 'small', 'span', 'strike', 'strong',
    'sub', 'sup', 'tt', 'u', 'var',
]

placeholder_tags = {'math': 'formula', 'code': 'codice'}

# Normalize title
def normalizeTitle(title):
    # remove leading whitespace and underscores
    title = title.strip(' _')
    # replace sequences of whitespace and underscore chars with a single space
    title = re.compile(r'[\s_]+').sub(' ', title)

    m = re.compile(r'([^:]*):(\s*)(\S(?:.*))').match(title)
    if m:
        prefix = m.group(1)
        if m.group(2):
            optionalWhitespace = ' '
        else:
            optionalWhitespace = ''
        rest = m.group(3)

        ns = prefix.capitalize()
        if ns in acceptedNamespaces:
            # If the prefix designates a known namespace, then it might be
            # followed by optional whitespace that should be removed to get
            # the canonical page name
            # (e.g., "Category:  Births" should become "Category:Births").
            title = ns + ":" + rest.capitalize()
        else:
            # No namespace, just capitalize first letter.
            # If the part before the colon is not a known namespace, then we must
            # not remove the space after the colon (if any), e.g.,
            # "3001: The_Final_Odyssey" != "3001:The_Final_Odyssey".
            # However, to get the canonical page name we must contract multiple
            # spaces into one, because
            # "3001:   The_Final_Odyssey" != "3001: The_Final_Odyssey".
            title = prefix.capitalize() + ":" + optionalWhitespace + rest
    else:
        # no namespace, just capitalize first letter
        title = title.capitalize()
    return title

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.


def unescape(text):
    def fixup(m):
        text = m.group(0)
        code = m.group(1)
        try:
            if text[1] == "#":  # character reference
                if text[2] == "x":
                    return chr(int(code[1:], 16))
                else:
                    return chr(int(code))
            else:               # named entity
                return chr(name2codepoint[code])
        except BaseException:
            return text  # leave as is

    return re.sub("&#?(\w+);", fixup, text)


# Match HTML comments
comment = re.compile(r'<!--.*?-->', re.DOTALL)

# Match elements to ignore
discard_element_patterns = []
for tag in discardElements:
    pattern = re.compile(
        r'<\s*%s\b[^>]*>.*?<\s*/\s*%s>' %
        (tag, tag), re.DOTALL | re.IGNORECASE)
    discard_element_patterns.append(pattern)

# Match ignored tags
ignored_tag_patterns = []


def ignoreTag(tag):
    left = re.compile(r'<\s*%s\b[^>]*>' % tag, re.IGNORECASE)
    right = re.compile(r'<\s*/\s*%s>' % tag, re.IGNORECASE)
    ignored_tag_patterns.append((left, right))


for tag in ignoredTags:
    ignoreTag(tag)

# Match selfClosing HTML tags
selfClosing_tag_patterns = []
for tag in selfClosingTags:
    pattern = re.compile(
        r'<\s*%s\b[^/]*/\s*>' %
        tag, re.DOTALL | re.IGNORECASE)
    selfClosing_tag_patterns.append(pattern)

# Match HTML placeholder tags
placeholder_tag_patterns = []
for tag, repl in list(placeholder_tags.items()):
    pattern = re.compile(
        r'<\s*%s(\s*| [^>]+?)>.*?<\s*/\s*%s\s*>' %
        (tag, tag), re.DOTALL | re.IGNORECASE)
    placeholder_tag_patterns.append((pattern, repl))

# Match preformatted lines
preformatted = re.compile(r'^ .*?$', re.MULTILINE)

# Match external links (space separates second optional parameter)
externalLink = re.compile(r'\[\w+.*? (.*?)\]')
externalLinkNoAnchor = re.compile(r'\[\w+[&\]]*\]')

# Matches bold/italic
bold_italic = re.compile(r"'''''([^']*?)'''''")
bold = re.compile(r"'''(.*?)'''")
italic_quote = re.compile(r"''\"(.*?)\"''")
italic = re.compile(r"''([^']*)''")
quote_quote = re.compile(r'""(.*?)""')

# Matches space
spaces = re.compile(r' {2,}')

# Matches dots
dots = re.compile(r'\.{4,}')

# A matching function for nested expressions, e.g. namespaces and tables.


def dropNested(text, openDelim, closeDelim):
    openRE = re.compile(openDelim)
    closeRE = re.compile(closeDelim)
    # partition text in separate blocks { } { }
    matches = []                # pairs (s, e) for each partition
    nest = 0                    # nesting level
    start = openRE.search(text, 0)
    if not start:
        return text
    end = closeRE.search(text, start.end())
    next = start
    while end:
        next = openRE.search(text, next.end())
        if not next:            # termination
            while nest:         # close all pending
                nest -= 1
                end0 = closeRE.search(text, end.end())
                if end0:
                    end = end0
                else:
                    break
            matches.append((start.start(), end.end()))
            break
        while end.end() < next.start():
            # { } {
            if nest:
                nest -= 1
                # try closing more
                last = end.end()
                end = closeRE.search(text, end.end())
                if not end:     # unbalanced
                    if matches:
                        span = (matches[0][0], last)
                    else:
                        span = (start.start(), last)
                    matches = [span]
                    break
            else:
                matches.append((start.start(), end.end()))
                # advance start, find next close
                start = next
                end = closeRE.search(text, next.end())
                break           # { }
        if next != start:
            # { { }
            nest += 1
    # collect text outside partitions
    res = ''
    start = 0
    for s, e in matches:
        res += text[start:s]
        start = e
    res += text[start:]
    return res


def dropSpans(matches, text):
    """Drop from text the blocks identified in matches"""
    matches.sort()
    res = ''
    start = 0
    for s, e in matches:
        res += text[start:s]
        start = e
    res += text[start:]
    return res


# Match interwiki links, | separates parameters.
# First parameter is displayed, also trailing concatenated text included
# in display, e.g. s for plural).
#
# Can be nested [[File:..|..[[..]]..|..]], [[Category:...]], etc.
# We first expand inner ones, than remove enclosing ones.
#
wikiLink = re.compile(r'\[\[([^[]*?)(?:\|([^[]*?))?\]\](\w*)')

parametrizedLink = re.compile(r'\[\[.*?\]\]')

# Function applied to wikiLinks


def make_anchor_tag(match):
    global keepLinks
    link = match.group(1)
    colon = link.find(':')
    if colon > 0 and link[:colon] not in acceptedNamespaces:
        return ''
    trail = match.group(3)
    anchor = match.group(2)
    if not anchor:
        anchor = link
    anchor += trail
    if keepLinks:
        return '<a href="%s">%s</a>' % (link, anchor)
    else:
        return anchor


def clean(text):

    # FIXME: templates should be expanded
    # Drop transclusions (template, parser functions)
    # See: http://www.mediawiki.org/wiki/Help:Templates
    text = dropNested(text, r'{{', r'}}')

    # Drop tables
    text = dropNested(text, r'{\|', r'\|}')

    # Expand links
    text = wikiLink.sub(make_anchor_tag, text)
    # Drop all remaining ones
    text = parametrizedLink.sub('', text)

    # Handle external links
    text = externalLink.sub(r'\1', text)
    text = externalLinkNoAnchor.sub('', text)

    # Handle bold/italic/quote
    text = bold_italic.sub(r'\1', text)
    text = bold.sub(r'\1', text)
    text = italic_quote.sub(r'&quot;\1&quot;', text)
    text = italic.sub(r'&quot;\1&quot;', text)
    text = quote_quote.sub(r'\1', text)
    text = text.replace("'''", '').replace("''", '&quot;')

    ################ Process HTML ###############

    # turn into HTML
    text = unescape(text)
    # do it again (&amp;nbsp;)
    text = unescape(text)

    # Collect spans

    matches = []
    # Drop HTML comments
    for m in comment.finditer(text):
        matches.append((m.start(), m.end()))

    # Drop self-closing tags
    for pattern in selfClosing_tag_patterns:
        for m in pattern.finditer(text):
            matches.append((m.start(), m.end()))

    # Drop ignored tags
    for left, right in ignored_tag_patterns:
        for m in left.finditer(text):
            matches.append((m.start(), m.end()))
        for m in right.finditer(text):
            matches.append((m.start(), m.end()))

    # Bulk remove all spans
    text = dropSpans(matches, text)

    # Cannot use dropSpan on these since they may be nested
    # Drop discarded elements
    for pattern in discard_element_patterns:
        text = pattern.sub('', text)

    # Expand placeholders
    for pattern, placeholder in placeholder_tag_patterns:
        index = 1
        for match in pattern.finditer(text):
            text = text.replace(match.group(), '%s_%d' % (placeholder, index))
            index += 1

    text = text.replace('<<', 'Â«').replace('>>', 'Â»')

    #######################################

    # Drop preformatted
    # This can't be done before since it may remove tags
    text = preformatted.sub('', text)

    # Cleanup text
    text = text.replace('\t', ' ')
    text = spaces.sub(' ', text)
    text = dots.sub('...', text)
    text = re.sub(' (,:\.\)\]Â»)', r'\1', text)
    text = re.sub('(\[\(Â«) ', r'\1', text)
    text = re.sub(r'\n\W+?\n', '\n', text)  # lines with only punctuations
    text = text.replace(',,', ',').replace(',.', '.')
    re2 = re.compile(r"__[A-Z]+__")
    text = re2.sub("", text)
    # Add other filters here

    return text


section = re.compile(r'(==+)\s*(.*?)\s*\1')


def compact(text, structure=False):
    """Deal with headers, lists, empty sections, residuals of tables"""
    page = []                   # list of paragraph
    headers = {}                # Headers for unfilled sections
    emptySection = False        # empty sections are discarded
    inList = False              # whether opened <UL>

    for line in text.split('\n'):

        if not line:
            continue
        # Handle section titles
        m = section.match(line)
        if m:
            title = m.group(2)
            lev = len(m.group(1))
            if structure:
                page.append("<h%d>%s</h%d>" % (lev, title, lev))
            if title and title[-1] not in '!?':
                title += '.'
            headers[lev] = title
            # drop previous headers
            for i in list(headers.keys()):
                if i > lev:
                    del headers[i]
            emptySection = True
            continue
        # Handle page title
        if line.startswith('++'):
            title = line[2:-2]
            if title:
                if title[-1] not in '!?':
                    title += '.'
                page.append(title)
        # handle lists
        elif line[0] in '*#:;':
            if structure:
                page.append("<li>%s</li>" % line[1:])
            else:
                continue
        # Drop residuals of lists
        elif line[0] in '{|' or line[-1] in '}':
            continue
        # Drop irrelevant lines
        elif (line[0] == '(' and line[-1] == ')') or line.strip('.-') == '':
            continue
        elif len(headers):
            items = list(headers.items())
            items.sort()
            for (i, v) in items:
                page.append(v)
            headers.clear()
            page.append(line)   # first line
            emptySection = False
        elif not emptySection:
            page.append(line)

    return page


def handle_unicode(entity):
    numeric_code = int(entity[2:-1])
    if numeric_code >= 0x10000:
        return ''
    return chr(numeric_code)

#------------------------------------------------------------------------------


class OutputSplitter:
    def __init__(self, max_file_size, path_name, segment=False):
        self.dir_index = 0
        self.file_index = 0
        self.max_file_size = max_file_size
        self.path_name = path_name
        self.segment = segment
        if sys.version_info[:2] == (3, 3):
            self.isoutdated = False
        else:
            self.isoutdated = True
        self.out_file = self.open_next_file()

    def reserve(self, size):
        cur_file_size = self.out_file.tell()

    def write(self, text):
        if self.segment:
            self.out_file.write(text)
        else:
            return

    def close(self):
        self.out_file.close()

    def open_next_file(self):
        self.file_index = self.file_index
        if self.file_index == 100:
            self.dir_index += 1
            self.file_index = 0
        file_name = 'wiki.txt'

        return open(file_name, 'a')

    def dir_name(self):
        # split into two kinds of directories:
        ### sentences_AA and structure_AA

        prefix = "sentences_" if self.segment else "structure_"

        char1 = self.dir_index % 26
        char2 = self.dir_index / 26 % 26
        return os.path.join(
            self.path_name, prefix + '%c%c' %
            (ord('A') + char2, ord('A') + char1))

    def file_name(self):
        return 'wiki_%02d' % self.file_index

### READER #############################################################


tagRE = re.compile(r'(.*?)<(/?\w+)[^>]*>(?:([^<]*)(<.*?>)?)?')


def process_data(ftype, input, output_sentences, output_structure,
                 vital_titles=None, vital_tags=None):
    global prefix
    page = []
    id = None
    inText = False
    redirect = False
    for line in input:
        if ftype != 'xml':
            line = str(line.decode('utf-8'))
        tag = ''
        if '<' in line:
            m = tagRE.search(line)
            if m:
                tag = m.group(2)
        if tag == 'page':
            page = []
            redirect = False
        elif tag == 'id' and not id:
            id = m.group(3)
        elif tag == 'title':
            title = m.group(3)
        elif tag == 'redirect':
            redirect = True
        elif tag == 'text':
            inText = True
            line = line[m.start(3):m.end(3)] + '\n'
            page.append(line)
            if m.lastindex == 4:  # open-close
                inText = False
        elif tag == '/text':
            if m.group(1):
                page.append(m.group(1) + '\n')
            inText = False
        elif inText:
            page.append(line)
        elif tag == '/page':
            colon = title.find(':')
            if (colon < 0 or title[:colon] in acceptedNamespaces) and \
                    not redirect:
                if (not vital_titles) or (title in vital_titles):
                    sys.stdout.flush()
                    tags = vital_tags[title] if vital_tags else []
                    WikiDocumentSentences(output_sentences, id, title, tags,
                                          ''.join(page))
                    #WikiDocument(output_structure, id, title, ''.join(page))
            id = None
            page = []
        elif tag == 'base':
            # discover prefix from the xml dump file
            # /mediawiki/siteinfo/base
            base = m.group(3)
            prefix = base[:base.rfind("/")]

# --------------------------------------
# Modified coverage.py scirpt from:
# https://svn.code.sf.net/p/apertium/svn/trunk/apertium-tools/coverage.py

def tokenize(corpusPath, automorfPath):
    tokenizedCorpus = tempfile.TemporaryFile()
    pipeline([
        ['cat', corpusPath],
        ['apertium-destxt'],
        ['lt-proc', '-w', automorfPath],
        ['apertium-retxt'],
        ['sed', r's/\$\W*\^/$\n^/g']
    ], tokenizedCorpus)

    return tokenizedCorpus


def getTotal(tokenizedCorpus):
    tokenizedCorpus.seek(0)
    return int(subprocess.check_output(['wc', '-l'], stdin=tokenizedCorpus))


def getKnown(tokenizedCorpus):
    tokenizedCorpus.seek(0)
    p1 = subprocess.Popen(['grep', '-v', '*'],
                          stdout=subprocess.PIPE, stdin=tokenizedCorpus)
    return int(subprocess.check_output(['wc', '-l'], stdin=p1.stdout))


def getStats(corpusPath, automorfPath):
    print('Calculating coverage... It may take a while.')
    tokenizedCorpus = tokenize(corpusPath, automorfPath)
    known, total = getKnown(tokenizedCorpus), getTotal(tokenizedCorpus)
    tokenizedCorpus.close()
    return known, total


def pipeline(commands, procOut, procIn=None):
    proc = None
    for n, command in enumerate(commands):
        lastCommand = n == len(commands) - 1
        stdin = proc.stdout if proc is not None else procIn
        stdout = subprocess.PIPE if not lastCommand else procOut
        proc = subprocess.Popen(command, stdin=stdin, stdout=stdout)
        if lastCommand:
            return proc.communicate()

# -------------------------------------
# Making all this together

"""def get_argparser():
    parser = argparse.ArgumentParser(description='AutoCoverage')
    parser.add_argument(
        '--lang',
        type=str,
        required=False,
        help="Specifies 2 or 3 letter language symbol; e.g. en or eng for English, pl or pol for Polish, etc.")
    parser.add_argument(
        '--dest',
        type=str,
        required=False,
        help="Specifies destination directory to download and compile the language module specified in --lang. If the directory already contains the module, it will be updated.")
    parser.add_argument(
        '--docker',
        action='store_true',
        required=False,
        help="Runs in docker instance.")

    # DONT USE THIS PARAMETER, ITS RAN THROUGH THE DOCKER INSTANCE
    parser.add_argument(
        '--is_docker_instance',
        action='store_true',
        required=False,
        help=argparse.SUPPRESS)

    parser.set_defaults(lang='')
    parser.set_defaults(dest='')
    parser.set_defaults(docker=False)

    parser.set_defaults(is_docker_instance=False)
    return parser"""


def DockerInstance(docker_directory, lang_2, lang_3):
    print('Downloading packages for Docker instance...')
    with open('Dockerfile', 'w') as f:
        f.write(docker_script.format(lang_3, lang_2))
    os.system('sudo docker build -t auto-coverage .')

    print('Running Docker...')
    os.system('sudo docker run auto-coverage')


def ReportHook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count * block_size * 100 / total_size), 100)
    sys.stdout.write("\r...{:.0f}%, {:.0f} MB, {:.0f} KB/s, {:.0f} seconds passed".format(percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()


def DownloadWiki(lang_code_2, lang_code_3, lang_path, docker):
    if docker:
        lang_path = lang_path + 'apertium-' + lang_code_3
    else:
        lang_path = lang_path + '/apertium-' + lang_code_3
    os.chdir(lang_path)
    url = 'https://dumps.wikimedia.org/' + lang_code_2 + 'wiki/'

    # Downloading wiki archive
    try:
        website = urllib.request.urlopen(url)
    except BaseException:
        print('Cannot find wiki archive for specified language!')
        sys.exit(1)
    read_website = website.read()
    # Get all hrefs on website
    urllist = re.findall(
        r"""<\s*a\s*href=["']([^=]+)["']""",
        read_website.decode("utf-8"))
    print('Downloading wiki archive...')

    archive_url = url + urllist[-2] + lang_code_2 + 'wiki-' + \
        urllist[-2].replace('/', '') + '-pages-articles-multistream.xml.bz2'

    try:
        urllib.request.urlretrieve(archive_url, os.getcwd() + '/' + lang_code_2 + 'wiki.txt.bz2', ReportHook)
    except urllib.error.HTTPError:
        print('An error occured when downloading Wiki archive, check if specified language code is correct and try again.')
        sys.exit(1)

    archive_path = os.getcwd() + '/' + lang_code_2 + 'wiki.txt.bz2'

    print('\nDownloaded at ' + archive_path)
    return archive_path, lang_path


def CompileLang(lang_path, code):
    lang_path = lang_path + 'apertium-' + code
    os.chdir(lang_path)
    os.system('./autogen.sh')
    os.system('make')
    os.chdir('..')


def DownloadOrUpdateLang(lang, destination, docker):
    try:
        if destination != '':
            os.system(
                'svn co https://svn.code.sf.net/p/apertium/svn/languages/apertium-' +
                lang + '/ ' + destination + '/apertium-' + lang)
        else:
            os.system(
                'svn co https://svn.code.sf.net/p/apertium/svn/languages/apertium-' +
                lang + '/')
    except BaseException:
        print('An error occured when downloading language module!')
        sys.exit(1)

    if destination != '':
        os.chdir(destination + '/apertium-' + lang)
    else:
        os.chdir('apertium-' + lang)

    if not docker:
        os.system('./autogen.sh')
        os.system('make')

    os.chdir('..')

    return os.getcwd()

def CountWords(wikiPath):
    words = 0
    with open(wikiPath, 'r') as f:
        for word in f.read().split(' '):
            words += 1
    return words


def StartScript(docker, is_docker_instance, destination, lang_3):
    docker_directory = os.getcwd()

    if destination != '':
        if destination.endswith('/'):
            destination = destination[:-1]

    if destination != '' and docker:
        print('Cannot use --dest parameter when running inside the docker instance!')
        sys.exit(1)

    try:
        lang_2 = ISO_639_3_TO_1[lang_3]
    except BaseException:
        if len(lang_3) == 3:
            lang_2 = lang_3
        elif len(lang_3) == 2:
            new_iso_converter = {v: k for k, v in ISO_639_3_TO_1.items()}
            lang_2 = lang_3
            lang_3 = new_iso_converter[lang_3]
        else:
            print('No specified language module!')
            sys.exit(1)

    lang_path = ''
    if not is_docker_instance:
        lang_path = DownloadOrUpdateLang(lang_3, destination, docker)
    else:
        lang_path = os.getcwd()
        CompileLang(lang_path, lang_3)

    if docker:
        DockerInstance(docker_directory, lang_2, lang_3)
        sys.exit(1)

    wiki_path, lang_path = DownloadWiki(lang_2, lang_3, lang_path, docker)

    # ------------------------
    global keepLinks, keepSections, prefix, acceptedNamespaces
    script_name = os.path.basename(sys.argv[0])

    #parser = get_argparser()
    #args = parser.parse_args()
    keepSections = True

    file_size = 500 * 1024
    output_dir = '.'

    if not keepLinks:
        ignoreTag('a')

    vital_titles = None
    vital_tags = None

    print('Processing wiki archive...')
    output_sentences = OutputSplitter(file_size, output_dir,
                                      segment=True)
    fname = wiki_path
    f = bz2.BZ2File(fname, mode='r')
    process_data('bzip2', f, output_sentences, vital_titles, vital_tags)
    output_sentences.close()
    wiki_path = wiki_path.replace(wiki_path.split('/')[-1], 'wiki.txt')
    print('Wiki archive processed.')
    # ------------------------

    automorfPath = lang_path + '/' + lang_3 + '.automorf.bin'

    known, total = getStats(wiki_path, automorfPath)

    if is_docker_instance:
        os.system('exit')

    coverage = float(known / total * 100.0)
    print('Coverage: ' + str(coverage))

    return wiki_path, coverage

"""def main():
    parser = get_argparser()
    args = parser.parse_args()

    docker = args.docker
    is_docker_instance = args.is_docker_instance
    destination = args.dest

    lang_3 = args.lang

    if lang_3 == '':
        print('The --lang parameter is required!')

    wiki_path, coverage = StartScript(docker, is_docker_instance, destination, lang_3)

if __name__ == '__main__':
    main()"""
