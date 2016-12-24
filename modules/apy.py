#!/usr/bin/env python
# coding=utf-8
'''
apy.py - Apertium APy Module
'''

import re
import urllib.request
import json
import web
from tools import GrumbleError, translate
from modules import more
import operator
from humanize import naturaldelta

headers = [(
    'User-Agent', 'Mozilla/5.0' +
    '(X11; U; Linux i686)' +
    'Gecko/20071127 Firefox/2.0.0.11'
)]

Apy_errorData = 'Sorry, Apertium APy did not return any data.'


def handle_error(error):
    response = error.read()
    err = json.loads(response.decode('utf-8'))
    if 'explanation' in err:
        raise GrumbleError('Error {:d}: {:s}'.format(err['code'], err['explanation']))
    raise GrumbleError('Error {:d}: {:s}'.format(err['code'], err['message']))


def check_no_data(resp_data):
    if not resp_data['responseData']:
        raise GrumbleError(APy_errorData)


def translate(phenny, translate_me, input_lang, output_lang='en'):
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    input_lang, output_lang = web.quote(input_lang), web.quote(output_lang)
    translate_me = web.quote(translate_me)

    try:
        response = opener.open(phenny.config.APy_url + '/translate?q=' + translate_me +
                               '&langpair=' + input_lang + '|' + output_lang).read()
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    responseArray = json.loads(response.decode('utf-8'))
    if responseArray['responseData']['translatedText'] == []:
        raise GrumbleError(Apy_errorData)

    translated_text = responseArray['responseData']['translatedText']
    return translated_text


def apertium_translate(phenny, input):
    '''Translates a phrase using APy.'''
    line = input.group(2)
    if not line:
        raise GrumbleError('Need something to translate!')

    pairs = []
    guidelines = line.split('|')
    if len(guidelines) > 1:
        for guideline in guidelines[1:]:
            pairs.append(guideline.strip().split('-'))
    guidelines = guidelines[0]
    stuff = re.search('(.*) ([a-z]+-[a-z]+)', guidelines)
    pairs.insert(0, stuff.group(2).split('-'))
    translate_me = stuff.group(1)

    if (len(translate_me) > 350) and (not input.admin):
        raise GrumbleError('Phrase must be under 350 characters.')

    msg = translate_me
    translated = ''
    for (input_lang, output_lang) in pairs:
        if input_lang == output_lang:
            raise GrumbleError('Stop trying to confuse me! Pick different languages ;)')
        msg = translate(phenny, msg, input_lang, output_lang)
        if not msg:
            raise GrumbleError('The {:s} to {:s} translation failed, sorry!'.format(input_lang, output_lang))
        msg = web.decode(msg)
        translated = msg

    phenny.reply(translated)

apertium_translate.name = 't'
apertium_translate.commands = ['t']
apertium_translate.example = '.t I like pie en-es'
apertium_translate.priority = 'high'


def apertium_listlangs(phenny, input):
    '''Lists languages available for translation from/to.'''
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open(phenny.config.APy_url+'/listPairs').read()
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    langs = json.loads(response.decode('utf-8'))
    check_no_data(langs)

    outlangs = []
    for pair in langs['responseData']:
        if pair['sourceLanguage'] not in outlangs:
            outlangs.append(pair['sourceLanguage'])
        if pair['targetLanguage'] not in outlangs:
            outlangs.append(pair['targetLanguage'])

    extra = '; more info: .listpairs lg'

    first = True
    allLangs = ''
    for lang in outlangs:
        if not first:
            allLangs += ', '
        else:
            first = False
        allLangs += lang
    phenny.say(allLangs + extra)

apertium_listlangs.name = 'listlangs'
apertium_listlangs.commands = ['listlangs']
apertium_listlangs.example = '.listlangs'
apertium_listlangs.priority = 'low'


def apertium_listpairs(phenny, input):
    '''Lists translation pairs available to apertium translation'''
    lang = input.group(2)

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open(phenny.config.APy_url+'/listPairs').read()
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    langs = json.loads(response.decode('utf-8'))
    check_no_data(langs)

    if not lang:
        allpairs = ''
        first = True
        for pair in langs['responseData']:
            if not first:
                allpairs += ','
            else:
                first = False
            allpairs += '{:s}  →  {:s}'.format(pair['sourceLanguage'], pair['targetLanguage'])
        phenny.say(allpairs)
    else:
        toLang = []
        fromLang = []
        for pair in langs['responseData']:
            if pair['sourceLanguage'] == lang:
                fromLang.append(pair['targetLanguage'])
            if pair['targetLanguage'] == lang:
                toLang.append(pair['sourceLanguage'])
        first = True
        froms = ''
        for lg in fromLang:
            if not first:
                froms += ', '
            else:
                first = False
            froms += lg
        first = True
        tos = ''
        for lg in toLang:
            if not first:
                tos += ', '
            else:
                first = False
            tos += lg
        finals = tos + ('  →  {:s}  →  '.format(lang)) + froms

        phenny.say(finals)

apertium_listpairs.name = 'listpairs'
apertium_listpairs.commands = ['listpairs']
apertium_listpairs.example = '.listpairs ca'
apertium_listpairs.priority = 'low'


def apertium_analyse(phenny, input):
    '''Analyse text using Apertium APy'''
    lang, text = input.groups()

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_analyseURL + '/analyse?lang=' + web.quote(lang)
    constructed_url += '&q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    jobj = json.loads(response.decode('utf-8'))
    messages = []
    for analysis, original in jobj:
        messages.append(original + '  →  ' + analysis)

    more.add_messages(input.nick, phenny,
                      '\n'.join(messages),
                      break_up=lambda x, y: x.split('\n'))

apertium_analyse.name = 'analyse'
apertium_analyse.rule = r'\.analy[sz]e\s(\S*)\s(.*)'
apertium_analyse.example = '.analyse kaz Сен бардың ба'
apertium_analyse.priority = 'medium'


def apertium_generate(phenny, input):
    '''Use Apertium APy's generate functionality'''
    lang, text = input.groups()

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_analyseURL + '/generate?lang=' + web.quote(lang)
    constructed_url += '&q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    jobj = json.loads(response.decode('utf-8'))
    messages = []
    for generation, original in jobj:
        messages.append(original + '  →  ' + generation)

    more.add_messages(input.nick, phenny, '\n'.join(messages), break_up=lambda x, y: x.split('\n'))

apertium_generate.name = 'generate'
apertium_generate.rule = r'\.(?:generate|gen)\s(\S*)\s(.*)'
apertium_generate.example = '.gen kaz ^сен<v><tv><imp><p2><sg>$'
apertium_generate.priority = 'medium'


def apertium_identlang(phenny, input):
    '''Identify the language for a given input.'''
    text = input.group(1)

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_url + '/identifyLang?q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
        jsdata = json.loads(response.decode('utf-8'))
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    messages = []
    for key, value in jsdata.items():
        messages.append(key + ' = ' + str(value))
    more.add_messages(input.nick, phenny, '\n'.join(messages), break_up=lambda x, y: x.split('\n'))

apertium_identlang.name = 'identlang'
apertium_identlang.commands = ['identlang']
apertium_identlang.example = '.identlang Whereas disregard and contempt for which have outraged the conscience of mankind'
apertium_identlang.priority = 'high'


def apertium_stats(phenny, input):
    '''Fetch function and usage statistics from APy.'''
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_url + '/stats'

    try:
        response = opener.open(constructed_url).read()
        jdata = json.loads(response.decode('utf-8'))
        periodStats = jdata['responseData']['periodStats']
        runningPipes = jdata['responseData']['runningPipes']
        holdingPipes = jdata['responseData']['holdingPipes']
        useCount = jdata['responseData']['useCount']
        uptime = jdata['responseData']['uptime']
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    # rudimentary pluralizer
    def plural(num, word, be=False):
        if num == 1:
            if be:
                return 'is ' + str(num) + ' ' + word
            return str(num) + ' ' + word
        if be:
            return 'are ' + str(num) + ' ' + word + 's'
        return str(num) + ' ' + word + 's'

    phenny.say('In the last hour, APy has processed {:s}, totalling {:s} '
               'and {:.2f} seconds, averaging {:.2f} characters per second.'.format(
                   plural(periodStats['requests'], 'request'), plural(periodStats['totChars'], 'character'),
                   periodStats['totTimeSpent'], periodStats['charsPerSec']))
    phenny.say('There {:s}:'.format(plural(len(runningPipes), 'running translation pipe', be=True)))
    for langs in runningPipes:
        phenny.say('  {:s}: {:s}, used {:s}'.format(
            langs, plural(runningPipes[langs], 'instance'), plural(useCount[langs], 'time')))
    phenny.say('There {:s}.'.format(plural(holdingPipes, 'holding pipe', be=True)))
    phenny.say('APy has been up for {:s}.'.format(naturaldelta(uptime)))

apertium_stats.name = 'apystats'
apertium_stats.commands = ['apystats']
apertium_stats.example = '.apystats'
apertium_stats.priority = 'low'


def apertium_calccoverage(phenny, input):
    '''Calculate translation coverage for a language and a given input.'''
    lang, text = input.groups()

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_url + '/calcCoverage?lang=' + web.quote(lang)
    constructed_url += '&q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    jsdata = json.loads(response.decode('utf-8'))
    phenny.say('Coverage is {:.1%}'.format(jsdata[0]))

apertium_calccoverage.name = 'calccoverage'
apertium_calccoverage.rule = '.calccoverage\s(\S*)\s(.*)'
apertium_calccoverage.example = '.calccoverage en-es Whereas disregard and contempt for which have outraged the conscience of mankind'
apertium_calccoverage.priority = 'medium'


def apertium_perword(phenny, input):
    '''Perform APy's tagger, morph, translate, and biltrans functions on individual words.'''
    valid_funcs = ['tagger', 'disambig', 'biltrans', 'translate', 'morph']

    # validate requested functions
    funcs = input.group(2).split(' ')
    for func in funcs:
        if func not in valid_funcs:
            phenny.say('The requested functions must be from the set ' + str(valid_funcs) + '.')
            return

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    request_url = phenny.config.APy_url + '/perWord?lang=' + web.quote(input.group(1)) + '&modes='
    for func in funcs[:-1]:
        request_url += func + '+'
    request_url += funcs[-1]
    request_url += '&q=' + web.quote(input.group(3))

    try:
        response = opener.open(request_url).read()
    except urllib.error.HTTPError as error:
        handle_error(error)
        return

    jsdata = json.loads(response.decode('utf-8'))
    for word in jsdata:
        phenny.say(word['input'] + ':')
        for func in funcs:
            msg = '  {:9s}: '.format(func)
            for out in word[func]:
                msg += '{:s} '.format(out)
            phenny.say(msg)

apertium_perword.name = 'perword'
apertium_perword.rule = '.perword\s(\S+)\s\((.+)\)\s(.+)'
apertium_perword.example = '.perword fr (tagger morph) Bonjour tout le monde!'
apertium_perword.priority = 'medium'
