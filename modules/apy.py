#!/usr/bin/env python
# coding=utf-8
'''
apy.py - Apertium APy Module
'''

import re
import urllib.request
import json
import web
from tools import GrumbleError
from modules import more
import operator
from humanize import naturaldelta

headers = [(
    'User-Agent', 'Mozilla/5.0' +
    '(X11; U; Linux i686)' +
    'Gecko/20071127 Firefox/2.0.0.11'
)]

Apy_errorData = 'Sorry, Apertium APy did not return any data.'
langRE = r'[a-z]{2,3}(?:_[A-Za-z]+)?'

SYNTAX_ERROR = 1

def strict_check(pattern, string, function):
    error = ''

    if not string:
        error = 'Usage: {}'.format(function.example)

    string = re.fullmatch(pattern, string)

    if not string:
        error = 'Usage: {}'.format(function.example)

    return string, error


def handle_error(error):
    response = error.read()
    err = json.loads(response.decode('utf-8'))
    if 'explanation' in err:
        raise GrumbleError('Error {:d}: {:s}'.format(err['code'], err['explanation'])) from error
    raise GrumbleError('Error {:d}: {:s}'.format(err['code'], err['message'])) from error


def check_no_data(resp_data):
    if not resp_data['responseData']:
        raise GrumbleError(APy_errorData)


def translate(phenny, translate_me, input_lang, output_lang='en'):
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    input_lang, output_lang = web.quote(input_lang), web.quote(output_lang)
    translate_me = web.quote(translate_me)

    try:
        apy_url = phenny.config.APy_url
    except:
        apy_url = 'http://apy.projectjj.com'

    try:
        response = opener.open('{:s}/translate?q={:s}&langpair={:s}|{:s}'.format(
            apy_url, translate_me, input_lang, output_lang)).read()
    except urllib.error.HTTPError as error:
        handle_error(error)

    responseArray = json.loads(response.decode('utf-8'))

    if responseArray['responseData']['translatedText'] == []:
        raise GrumbleError(Apy_errorData)

    translated_text = responseArray['responseData']['translatedText']
    return translated_text


def apertium_translate(phenny, input):
    '''Translates a phrase using APy.'''
    pairRE = langRE + r'-' + langRE
    line, line_error = strict_check(r'((?:' + pairRE + r'(?:\|' + pairRE + r')*' + r' ?)+)\s+(.*)',
                        input.group(1), apertium_translate)
    
    if line_error:
        phenny.say(line_error)
        return SYNTAX_ERROR

    if (len(line.group(2)) > 350) and (not input.admin):
        #raise GrumbleError('Phrase must be under 350 characters.')
        phenny.say('Phrase must be under 350 characters.')
        return SYNTAX_ERROR

    blocks = line.group(1).split(' ')
    for block in blocks:
        pairs = block.split('|')
        translated = line.group(2)
        for (input_lang, output_lang) in [pair.split('-') for pair in pairs]:
            if input_lang == output_lang:
                #raise GrumbleError('Stop trying to confuse me! Pick different languages ;)')
                phenny.say('Stop trying to confuse me! Pick different languages ;)')
                return SYNTAX_ERROR
            
            # TODO: Remove this try/except block? web.decode doesn't seem to raise any GrumbleError's
            try:
                translated = web.decode(translate(phenny, translated, input_lang, output_lang))
            except GrumbleError as err:
                phenny.say('{:s}-{:s}: {:s}'.format(input_lang, output_lang, str(err)))
                return SYNTAX_ERROR
        phenny.reply(web.decode(translated))

apertium_translate.name = 't'
apertium_translate.commands = ['t']
apertium_translate.example = '.t en-es|es-fr en-ca I like pie'
apertium_translate.priority = 'high'


def apertium_listlangs(phenny, input):
    '''Lists languages available for translation from/to.'''
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open(phenny.config.APy_url + '/listPairs').read()
    except urllib.error.HTTPError as error:
        handle_error(error)

    langs = json.loads(response.decode('utf-8'))
    check_no_data(langs)

    outlangs = []
    for pair in langs['responseData']:
        if pair['sourceLanguage'] not in outlangs:
            outlangs.append(pair['sourceLanguage'])
        if pair['targetLanguage'] not in outlangs:
            outlangs.append(pair['targetLanguage'])

    phenny.say(', '.join(outlangs) + '; more info: .listpairs lg')

apertium_listlangs.name = 'listlangs'
apertium_listlangs.commands = ['listlangs']
apertium_listlangs.example = '.listlangs'
apertium_listlangs.priority = 'low'


def apertium_listpairs(phenny, input):
    '''Lists translation pairs available to apertium translation'''
    lang = input.group(1)

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open(phenny.config.APy_url + '/listPairs').read()
    except urllib.error.HTTPError as error:
        handle_error(error)

    langs = json.loads(response.decode('utf-8'))
    check_no_data(langs)

    if not lang:
        phenny.say(', '.join(map(lambda pair: '{:s}  →  {:s}'
                                 .format(pair['sourceLanguage'], pair['targetLanguage']),
                                 langs['responseData'])))
    else:
        toLang = []
        fromLang = []
        for pair in langs['responseData']:
            if pair['sourceLanguage'] == lang:
                fromLang.append(pair['targetLanguage'])
            if pair['targetLanguage'] == lang:
                toLang.append(pair['sourceLanguage'])
        phenny.say('{:s}  →  {:s}  →  {:s}'.format(', '.join(toLang), lang, ', '.join(fromLang)))

apertium_listpairs.name = 'listpairs'
apertium_listpairs.commands = ['listpairs']
apertium_listpairs.example = '.listpairs ca'
apertium_listpairs.priority = 'low'


def apertium_analyse(phenny, input):
    '''Analyse text using Apertium APy'''
    cmd, cmd_error = strict_check(r'(' + langRE + r')\s+(.*)', input.group(1), apertium_analyse)

    if cmd_error:
        phenny.say(cmd_error)
        return SYNTAX_ERROR

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open('{:s}/analyse?lang={:s}&q={:s}'.format(
            phenny.config.APy_analyseURL, web.quote(cmd.group(1)), web.quote(cmd.group(2).strip()))).read()
    except urllib.error.HTTPError as error:
        handle_error(error)

    jobj = json.loads(response.decode('utf-8'))
    messages = []

    for analysis, original in jobj:
        messages.append(original + '  →  ' + analysis)

    more.add_messages(phenny, input.nick, messages)

apertium_analyse.name = 'analyse'
apertium_analyse.commands = ['analyse', 'analyze']
apertium_analyse.example = '.analyse kaz Сен бардың ба'
apertium_analyse.priority = 'medium'


def apertium_generate(phenny, input):
    '''Use Apertium APy's generate functionality'''
    cmd, cmd_error = strict_check(r'(' + langRE + r')\s+(.*)', input.group(1), apertium_generate)

    if cmd_error:
        phenny.say(cmd_error)
        return SYNTAX_ERROR

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open('{:s}/generate?lang={:s}&q={:s}'.format(
            phenny.config.APy_analyseURL, web.quote(cmd.group(1)), web.quote(cmd.group(2).strip()))).read()
    except urllib.error.HTTPError as error:
        handle_error(error)

    jobj = json.loads(response.decode('utf-8'))
    messages = []

    for generation, original in jobj:
        messages.append(original + '  →  ' + generation)

    more.add_messages(phenny, input.nick, messages)

apertium_generate.name = 'generate'
apertium_generate.commands = ['generate']
apertium_generate.example = '.generate kaz ^сен<v><tv><imp><p2><sg>$'
apertium_generate.priority = 'medium'


def apertium_identlang(phenny, input):
    '''Identify the language for a given input.'''
    text, text_error = strict_check(r'.*', input.group(1), apertium_identlang)
    text = text.group(0)

    if text_error:
        phenny.say(text_error)
        return SYNTAX_ERROR

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open('{:s}/identifyLang?q={:s}'.format(
            phenny.config.APy_url, web.quote(text.strip()))).read()
        jsdata = json.loads(response.decode('utf-8'))
    except urllib.error.HTTPError as error:
        handle_error(error)

    messages = []

    for key, value in jsdata.items():
        messages.append(key + ' = ' + str(value))

    more.add_messages(phenny, input.nick, messages)

apertium_identlang.name = 'identlang'
apertium_identlang.commands = ['identlang']
apertium_identlang.example = '.identlang Whereas disregard and contempt for which have outraged the conscience of mankind'
apertium_identlang.priority = 'high'


def apertium_stats(phenny, input):
    '''Fetch function and usage statistics from APy.'''
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open(phenny.config.APy_url + '/stats').read()
    except urllib.error.HTTPError as error:
        handle_error(error)

    jdata = json.loads(response.decode('utf-8'))
    periodStats = jdata['responseData']['periodStats']
    runningPipes = jdata['responseData']['runningPipes']
    holdingPipes = jdata['responseData']['holdingPipes']
    useCount = jdata['responseData']['useCount']
    uptime = jdata['responseData']['uptime']

    # rudimentary pluralizer
    def plural(num, word, be=False):
        if num == 1:
            if be:
                return 'is {:d} {:s}'.format(num, word)
            return '{:d} {:s}'.format(num, word)
        if be:
            return 'are {:d} {:s}s'.format(num, word)
        return '{:d} {:s}s'.format(num, word)

    pipe = input.group(1)
    if pipe:
        runningPipes = jdata['responseData']['runningPipes']
        useCount = jdata['responseData']['useCount']
        if pipe in runningPipes:
            phenny.say('The {:s} pipe has {:s} and has been used {:s}.'.format(
                pipe, plural(runningPipes[pipe], 'instance'), plural(useCount[pipe], 'time')))
        else:
            phenny.say('There is no running pipe called {:s}. (You can run .apystats in a '
                       'private query for details about all pipes.)'.format(pipe))
        return

    phenny.say('In the last hour, APy has processed {:s}, totalling {:s} '
               'and {:.2f} seconds, averaging {:.2f} characters per second.'.format(
                   plural(periodStats['requests'], 'request'), plural(periodStats['totChars'], 'character'),
                   periodStats['totTimeSpent'], periodStats['charsPerSec']))

    if input.sender.startswith('#'):
        phenny.say('There {:s}.'.format(plural(len(runningPipes), 'running translation pipe', be=True)))
        phenny.say('(Run .apystats <pipe> for details about <pipe>, or '
                   'run .apystats in a private query for details about all pipes.)')
    else:
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
    cmd, cmd_error = strict_check(r'(' + langRE + r')\s+(.*)', input.group(1), apertium_calccoverage)

    if cmd_error:
        phenny.say(cmd_error)
        return SYNTAX_ERROR

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open('{:s}/calcCoverage?lang={:s}&q={:s}'.format(
            phenny.config.APy_url, web.quote(cmd.group(1)), web.quote(cmd.group(2).strip()))).read()
    except urllib.error.HTTPError as error:
        handle_error(error)

    jsdata = json.loads(response.decode('utf-8'))
    phenny.say('Coverage is {:.1%}'.format(jsdata[0]))

apertium_calccoverage.name = 'calccoverage'
apertium_calccoverage.commands = ['calccoverage', 'coverage']
apertium_calccoverage.example = '.calccoverage en Whereas disregard and contempt for which have outraged the conscience of mankind'
apertium_calccoverage.priority = 'medium'


def apertium_perword(phenny, input):
    '''Perform APy's tagger, morph, translate, and biltrans functions on individual words.'''
    cmd, cmd_error = strict_check(r'(' + langRE + r')\s+\((.*)\)\s+(.*)', input.group(1), apertium_perword)
    valid_funcs = {'tagger', 'disambig', 'biltrans', 'translate', 'morph'}

    if cmd_error:
        phenny.say(cmd_error)
        return SYNTAX_ERROR

    # validate requested functions
    funcs = cmd.group(2).split(' ')
    if not set(funcs) <= valid_funcs:
        raise GrumbleError('The requested functions must be from the set {:s}.'.format(str(valid_funcs)))

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open('{:s}/perWord?lang={:s}&modes={:s}&q={:s}'.format(
            phenny.config.APy_url, web.quote(cmd.group(1)), '+'.join(funcs), web.quote(cmd.group(3)))).read()
    except urllib.error.HTTPError as error:
        handle_error(error)

    jsdata = json.loads(response.decode('utf-8'))
    for word in jsdata:
        phenny.say(word['input'] + ':')
        for func in funcs:
            phenny.say('  {:9s}: {:s}'.format(func, ' '.join(word[func])))

apertium_perword.name = 'perword'
apertium_perword.commands = ['perword']
apertium_perword.example = '.perword fr (tagger morph) Bonjour tout le monde!'
apertium_perword.priority = 'medium'
