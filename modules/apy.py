#!/usr/bin/env python
# coding=utf-8
'''
apy.py - Apertium APy Module
'''

import re
import urllib.parse
import json
import web
from tools import GrumbleError
from modules import more
import operator
from humanize import naturaldelta
from bot import command

headers = [(
    'User-Agent', 'Mozilla/5.0' +
    '(X11; U; Linux i686)' +
    'Gecko/20071127 Firefox/2.0.0.11'
)]

Apy_errorData = 'Sorry, Apertium APy did not return any data.'
langRE = r'[a-z]{2,3}(?:_[A-Za-z]+)?'


def strict_check(pattern, string, function):
    error = ''

    if not string:
        error = 'Usage: {}'.format(function.example)

    string = re.fullmatch(pattern, string)

    if not string:
        error = 'Usage: {}'.format(function.example)

    return string, error


def check_no_data(resp_data):
    if not resp_data['responseData']:
        raise GrumbleError(APy_errorData)


def translate(phenny, translate_me, input_lang, output_lang='en'):
    input_lang, output_lang = web.quote(input_lang), web.quote(output_lang)
    translate_me = web.quote(translate_me)

    try:
        apy_url = phenny.config.APy_url
    except:
        apy_url = 'https://apertium.org/apy'

    responseArray = web.api_call(
        '{:s}/translate?q={:s}&langpair={:s}|{:s}'.format(
            apy_url, translate_me, input_lang, output_lang),
        headers=headers)

    if responseArray['responseData']['translatedText'] == []:
        raise GrumbleError(Apy_errorData)

    translated_text = responseArray['responseData']['translatedText']
    return translated_text

@command('t', priority='high', example='.t en-es|es-fr en-ca I like pie')
def apertium_translate(phenny, msg):
    '''Translates a phrase using APy.'''
    pairRE = langRE + r'-' + langRE
    line, line_error = strict_check(r'((?:' + pairRE + r'(?:\|' + pairRE + r')*' + r' ?)+)\s+(.*)',
                        msg.command_args, apertium_translate)

    if line_error:
        raise GrumbleError(line_error)
        return

    if (len(line.group(2)) > 350) and (not phenny.is_admin(msg.nick)):
        raise GrumbleError('Phrase must be under 350 characters.')
        #phenny.say('Phrase must be under 350 characters.')

    blocks = line.group(1).split(' ')
    for block in blocks:
        pairs = block.split('|')
        translated = line.group(2)
        for (input_lang, output_lang) in [pair.split('-') for pair in pairs]:
            if input_lang == output_lang:
                raise GrumbleError('Stop trying to confuse me! Pick different languages ;)')
                #phenny.say('Stop trying to confuse me! Pick different languages ;)')

            # TODO: Remove this try/except block? web.decode doesn't seem to raise any GrumbleError's
            try:
                translated = web.decode(translate(phenny, translated, input_lang, output_lang))
            except GrumbleError as err:
                phenny.say('{:s}-{:s}: {:s}'.format(input_lang, output_lang, str(err)))
                return
        phenny.reply(web.decode(translated))

@command('tweb', example='.tweb eng-spa https://scoopgracie.com/', priority='high')
def apertium_web_translate(phenny, msg):
    if ' ' not in msg.command_args:
        return
    pair, url = msg.command_args.split(' ', 1)
    pair = urllib.parse.quote_plus(pair)
    url = urllib.parse.quote_plus(url)
    phenny.say('Translated page at https://apertium.org/index.eng.html?dir={}&qP={}#webpageTranslation'.format(pair, url))

@command('listlangs', priority='low')
def apertium_listlangs(phenny, msg):
    '''Lists languages available for translation from/to.'''
    langs = web.api_call(phenny.config.APy_url + '/listPairs',
                         headers=headers)
    check_no_data(langs)

    outlangs = []
    for pair in langs['responseData']:
        if pair['sourceLanguage'] not in outlangs:
            outlangs.append(pair['sourceLanguage'])
        if pair['targetLanguage'] not in outlangs:
            outlangs.append(pair['targetLanguage'])

    phenny.say(', '.join(outlangs) + '; more info: .listpairs lg')

@command('listpairs', priority='low', example='.listpairs ca')
def apertium_listpairs(phenny, msg):
    '''Lists translation pairs available to apertium translation'''
    lang = msg.command_args
    langs = web.api_call(phenny.config.APy_url + '/listPairs',
                         headers=headers)
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

@command(['analyse', 'analyze'], example='.analyse kaz Сен бардың ба')
def apertium_analyse(phenny, msg):
    '''Analyse text using Apertium APy'''
    cmd, cmd_error = strict_check(r'(' + langRE + r')\s+(.*)', msg.command_args, apertium_analyse)

    if cmd_error:
        raise GrumbleError(cmd_error)
        return

    jobj = web.api_call(
        '{:s}/analyse?lang={:s}&q={:s}'.format(
            phenny.config.APy_analyseURL, web.quote(cmd.group(1)), web.quote(cmd.group(2).strip())),
        headers=headers)
    messages = []

    for analysis, original in jobj:
        messages.append(original + '  →  ' + analysis)

    more.add_messages(phenny, msg.nick, messages)

@command('generate', example='.generate kaz ^сен<v><tv><imp><p2><sg>$')
def apertium_generate(phenny, msg):
    '''Use Apertium APy's generate functionality'''
    cmd, cmd_error = strict_check(r'(' + langRE + r')\s+(.*)', msg.command_args, apertium_generate)

    if cmd_error:
        raise GrumbleError(cmd_error)
        return

    jobj = web.api_call(
        '{:s}/generate?lang={:s}&q={:s}'.format(
            phenny.config.APy_analyseURL, web.quote(cmd.group(1)), web.quote(cmd.group(2).strip())),
        headers=headers)
    messages = []

    for generation, original in jobj:
        messages.append(original + '  →  ' + generation)

    more.add_messages(phenny, msg.nick, messages)

@command('identlang', example='.identlang Whereas disregard and contempt for which have outraged the conscience of mankind')
def apertium_identlang(phenny, msg):
    '''Identify the language for a given input.'''
    text, text_error = strict_check(r'.*', msg.command_args, apertium_identlang)
    text = text.group(0)

    if text_error:
        phenny.say(text_error)
        return

    jsdata = web.api_call(
        '{:s}/identifyLang?q={:s}'.format(
            phenny.config.APy_url, web.quote(text.strip())),
        headers=headers)
    messages = []

    for key, value in jsdata.items():
        messages.append(key + ' = ' + str(value))

    more.add_messages(phenny, msg.nick, messages)

@command('apystats')
def apertium_stats(phenny, msg):
    '''Fetch function and usage statistics from APy.'''
    jdata = web.api_call(phenny.config.APy_url + '/stats', headers=headers)
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

    pipe = msg.command_args
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

    if msg.sender.startswith('#'):
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

@command(['calccoverage', 'coverage'], example='.calccoverage en Whereas disregard and contempt for which have outraged the conscience of mankind')
def apertium_calccoverage(phenny, msg):
    '''Calculate translation coverage for a language and a given input.'''
    cmd, cmd_error = strict_check(r'(' + langRE + r')\s+(.*)', msg.command_args, apertium_calccoverage)

    if cmd_error:
        raise GrumbleError(cmd_error)
        return

    jsdata = web.api_call(
        '{:s}/calcCoverage?lang={:s}&q={:s}'.format(
            phenny.config.APy_url, web.quote(cmd.group(1)), web.quote(cmd.group(2).strip())),
        headers=headers)
    phenny.say('Coverage is {:.1%}'.format(jsdata[0]))

@command('perword', example='.perword fr (tagger morph) Bonjour tout le monde!')
def apertium_perword(phenny, msg):
    '''Perform APy's tagger, morph, translate, and biltrans functions on individual words.'''
    cmd, cmd_error = strict_check(r'(' + langRE + r')\s+\((.*)\)\s+(.*)', msg.command_args, apertium_perword)
    valid_funcs = {'tagger', 'disambig', 'biltrans', 'translate', 'morph'}

    if cmd_error:
        raise GrumbleError(cmd_error)
        return

    # validate requested functions
    funcs = cmd.group(2).split(' ')
    if not set(funcs) <= valid_funcs:
        raise GrumbleError('The requested functions must be from the set {:s}.'.format(', '.join(sorted(valid_funcs))))

    jsdata = web.api_call(
        '{:s}/perWord?lang={:s}&modes={:s}&q={:s}'.format(
            phenny.config.APy_url, web.quote(cmd.group(1)), '+'.join(funcs), web.quote(cmd.group(3))),
        headers=headers)
    for word in jsdata:
        phenny.say(word['input'] + ':')
        for func in funcs:
            phenny.say('  {:9s}: {:s}'.format(func, ' '.join(word[func])))
