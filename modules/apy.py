#!/usr/bin/env python
# coding=utf-8
"""
apertium_translate.py - Phenny Translation Module
"""

import re
import urllib.request
import json
import web
from tools import GrumbleError, translate
from modules import more
import operator

headers = [(
    'User-Agent', 'Mozilla/5.0' +
    '(X11; U; Linux i686)' +
    'Gecko/20071127 Firefox/2.0.0.11'
)]

Apy_errorData = 'Sorry, apertium APy did not return any data ☹'
Apy_errorHttp = 'Sorry, apertium APy gave HTTP error %s: %s ☹'


def translate(phenny, translate_me, input_lang, output_lang='en'):
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    input_lang, output_lang = web.quote(input_lang), web.quote(output_lang)
    translate_me = web.quote(translate_me)

    response = opener.open(phenny.config.APy_url+'/translate?q='+translate_me+'&langpair='+input_lang+"|"+output_lang).read()

    responseArray = json.loads(response.decode('utf-8'))
    if int(responseArray['responseStatus']) != 200:
        raise GrumbleError(Apy_errorHttp % (responseArray['responseStatus'], responseArray['responseDetails']))
    if responseArray['responseData']['translatedText'] == []:
        raise GrumbleError(Apy_errorData)

    translated_text = responseArray['responseData']['translatedText']
    return translated_text

def apertium_translate(phenny, input):
    """Translates a phrase using APy."""
    line = input.group(2)
    if not line:
        raise GrumbleError("Need something to translate!")

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
    translated = ""
    for (input_lang, output_lang) in pairs:
        if input_lang == output_lang:
            raise GrumbleError('Stop trying to confuse me!  Pick different languages ;)')
        msg = translate(phenny, msg, input_lang, output_lang)
        if not msg:
            raise GrumbleError('The %s to %s translation failed, sorry!' % (input_lang, output_lang))
        msg = web.decode(msg)
        translated = msg

    phenny.reply(translated)

def apertium_listlangs(phenny, input):
    """Lists languages available for translation from/to."""
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    response = opener.open(phenny.config.APy_url+'/listPairs').read()

    langs = json.loads(response.decode('utf-8'))
    if int(langs['responseStatus']) != 200:
        raise GrumbleError(Apy_errorHttp % (langs['responseStatus'], langs['responseDetails']))
    if langs['responseData'] == []:
        raise GrumbleError(Apy_errorData)

    outlangs = []
    for pair in langs['responseData']:
        if pair['sourceLanguage'] not in outlangs:
            outlangs.append(pair['sourceLanguage'])
        if pair['targetLanguage'] not in outlangs:
            outlangs.append(pair['targetLanguage'])

    extra = "; more info: .listpairs lg"

    first = True
    allLangs = ""
    for lang in outlangs:
        if not first:
            allLangs += ", "
        else:
            first = False
        allLangs += lang
    phenny.say(allLangs + extra)

def apertium_listpairs(phenny, input):
    """Lists translation pairs available to apertium translation"""
    lang = input.group(2)

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    response = opener.open(phenny.config.APy_url+'/listPairs').read()

    langs = json.loads(response.decode('utf-8'))

    langs = json.loads(response.decode('utf-8'))
    if langs['responseData'] is []:
        raise GrumbleError(Apy_errorData)
    if int(langs['responseStatus']) != 200:
        raise GrumbleError(Apy_errorHttp % (langs['responseStatus'], langs['responseDetails']))

    if not lang:
        allpairs = ""
        first = True
        for pair in langs['responseData']:
            if not first:
                allpairs += ","
            else:
                first = False
            allpairs += "%s→%s" % (pair['sourceLanguage'], pair['targetLanguage'])
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
        froms = ""
        for lg in fromLang:
            if not first:
                froms += ", "
            else:
                first = False
            froms += lg
        first = True
        tos = ""
        for lg in toLang:
            if not first:
                tos += ", "
            else:
                first = False
            tos += lg
        finals = tos + (" → %s → " % lang) + froms

        phenny.say(finals)

def apertium_analyse(phenny, input):
    """Analyse text using Apertium APY"""
    lang, text = input.groups()

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_analyseURL + '/analyse?lang=' + web.quote(lang)
    constructed_url += '&q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
    except urllib.error.HTTPError as error:
        response = error.read()
        jobj = json.loads(response.decode('utf-8'))
        if 'explanation' in jobj:
            phenny.say('The following error occurred: ' + jobj['explanation'])
        else:
            phenny.say('An error occurred: ' + str(error))
        return

    jobj = json.loads(response.decode('utf-8'))
    messages = []
    for analysis, original in jobj:
        messages.append(original + " → " + analysis)

    more.add_messages(input.nick, phenny,
                      "\n".join(messages),
                      break_up=lambda x, y: x.split('\n'))

def apertium_generate(phenny, input):
    """Use Apertium APY's generate functionality"""
    lang, text = input.groups()

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_analyseURL + '/generate?lang=' + web.quote(lang)
    constructed_url += '&q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
    except urllib.error.HTTPError as error:
        response = error.read()
        jobj = json.loads(response.decode('utf-8'))
        if 'explanation' in jobj:
            phenny.say('The following error occurred: ' + jobj['explanation'])
        else:
            phenny.say('An error occurred: ' + str(error))
        return

    jobj = json.loads(response.decode('utf-8'))
    messages = []
    for generation, original in jobj:
        messages.append(original + " → " + generation)

    more.add_messages(input.nick, phenny,
        "\n".join(messages),
        break_up=lambda x, y: x.split('\n'))

def apertium_identlang(phenny, input):
    """Identify Language using Apertium APY"""
    lang, text = input.groups()

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_url + '/identifyLang?q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
        jsdata = json.loads(response.decode('utf-8'))
    except urllib.error.HTTPError as error:
        response = error.read()
        phenny.say(response)

    messages = []
    for key, value in jsdata.items():
        messages.append(key + " = " + str(value))
    more.add_messages(input.nick, phenny,
        "\n".join(messages),
        break_up=lambda x, y: x.split('\n'))

def apertium_stats(phenny, input):
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_url + '/stats'

    try:
        response = opener.open(constructed_url).read()
        jdata = json.loads(response.decode('utf-8'))
        holdingPipes = jdata['responseData']['holdingPipes']
        uptime = jdata['responseData']['uptime']
        periodStats = jdata['responseData']['periodStats']
        useCount = jdata['responseData']['useCount']
    except urllib.error.HTTPError as error:
        response = error.read()
        phenny.say(response)

    messages = []
    for key, value in periodStats.items():
        messages.append(key + " = " + str(value))
    f_message = "HoldingPipes: " + str(holdingPipes) + " UpTime: " + str(uptime) + " Period Stats: " + " ".join(messages)
    messages = []
    for key, value in useCount.items():
        messages.append(key + " = " + str(value))
    lines = sorted(useCount.items(), key=operator.itemgetter(1),reverse=True)

    n_lines = []
    for x in lines:
        n_lines.append("".join(str(x))
            .replace("(", "")
            .replace(")", "")
            .replace("'", "")
            .replace(",", ":"))

    max_length = 428
    for y in range(len(n_lines)):
         rs = f_message + " Use Count: " + ", ".join(n_lines[:y+1])
         if len(rs) + 2 + len(n_lines[y+1]) >= max_length:
             break

    phenny.say(rs)

def apertium_calccoverage(phenny, input):
    """Get Coverage using Apertium APY"""
    lang, text = input.groups()

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    constructed_url = phenny.config.APy_url + '/getCoverage?lang=' + web.quote(lang)
    constructed_url += '&q=' + web.quote(text.strip())

    try:
        response = opener.open(constructed_url).read()
        jsdata = json.loads(response.decode('utf-8'))
    except urllib.error.HTTPError as error:
        response = error.read()
        phenny.say(response)
    messages = []
    for key, value in jsdata.items():
        messages.append(key + " = " + str(value))
    more.add_messages(input.nick, phenny,
        "\n".join(messages),
        break_up=lambda x, y: x.split('\n'))

apertium_listpairs.name = 'listpairs'
apertium_listpairs.commands = ['listpairs']
apertium_listpairs.example = '.listpairs ca'
apertium_listpairs.priority = 'low'

apertium_listlangs.name = 'listlangs'
apertium_listlangs.commands = ['listlangs']
apertium_listlangs.example = '.listlangs'
apertium_listlangs.priority = 'low'

apertium_translate.name = 't'
apertium_translate.commands = ['t']
apertium_translate.example = '.t I like pie en-es'
apertium_translate.priority = 'high'

apertium_analyse.name = 'analyse'
apertium_analyse.rule = r'\.analy[sz]e\s(\S*)\s(.*)'
apertium_analyse.example = '.analyse kaz Сен бардың ба'
apertium_analyse.priority = 'high'

apertium_generate.name = 'generate'
apertium_generate.rule = r'\.(?:generate|gen)\s(\S*)\s(.*)'
apertium_generate.example = '.gen kaz ^сен<v><tv><imp><p2><sg>$'
apertium_generate.priority = 'high'

apertium_identlang.name = 'identlang'
apertium_identlang.commands = ['identlang']
apertium_identlang.example = '.identlang Whereas disregard and contempt for which have outraged the conscience of mankind'
apertium_identlang.priority = 'high'

apertium_stats.name = 'apystats'
apertium_stats.commands = ['apystats']
apertium_stats.example = '.apystats'
apertium_stats.priority = 'high'

apertium_calccoverage.name = 'calccoverage'
apertium_calccoverage.commands = ['calccoverage']
apertium_calccoverage.example = '.calccoverage en-es Whereas disregard and contempt for which have outraged the conscience of mankind'
apertium_calccoverage.priority = 'high'
