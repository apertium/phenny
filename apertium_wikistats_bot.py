#!/usr/bin/env python3

import argparse
import requests
import json
import logging
import sys
import re
import os
import subprocess
import shutil
import importlib
import urllib.request
import collections
import tempfile
import xml.etree.ElementTree as etree
import datetime
import autocoverage

wikiURL = 'http://wiki.apertium.org/wiki/'
apiURL = 'http://wiki.apertium.org/w/api.php'
statsURL = 'http://apertium.projectjj.com/stats-service/apertium-%s/?async=false'
githubBlobUrl = 'https://raw.githubusercontent.com/apertium/%s/master/%s'
githubCommitUrl = 'https://raw.githubusercontent.com/apertium/%s/%s/%s'

s = requests.Session()

fileStatTypeMapping = {
    'Monodix': {'Stems': 'stems', 'Paradigms': 'paradigms'},
    'MetaMonodix': {'Stems': 'meta stems', 'Paradigms': 'meta paradigms'},
    'Bidix': {'Entries': 'stems'},
    'MetaBidix': {'Stems': 'meta stems'},
    'Lexc': {'Stems': 'stems', 'VanillaStems': 'vanilla stems'},
    'Rlx': {'Rules': 'rules'},
    'Transfer': {'Rules': 'rules', 'Macros': 'macros'}
}

# https://docs.python.org/3.8/library/string.html#format-examples
def formatNumberThousands(number):
    return '{:,}'.format(number)

def getStats(rawStats, monoLang):
    if not rawStats:
        return {}

    fileCounts = {}
    for stat in rawStats:
        fileFormat = stat['file_kind']
        filePath = stat['path']
        statName = stat['name']
        statKind = stat['stat_kind']
        if fileFormat in fileStatTypeMapping and statKind in fileStatTypeMapping[fileFormat]:
            splitFilePath = filePath.split('.')
            countType = fileStatTypeMapping[fileFormat][statKind]
            wikiKey = splitFilePath[-1] + ' ' + countType
            if not monoLang:
                countType = splitFilePath[1] + ' ' + wikiKey
            revisionInfo = (githubCommitUrl % (statName, stat['sha'], filePath), stat['last_author'], stat['sha'][:6])

            statValue = int(stat['value'])
            statValue = formatNumberThousands(statValue)
            
            fileCounts[countType] = (statValue, revisionInfo, githubBlobUrl % (statName, filePath))
    return fileCounts

def getJSONFromStatsService(lang):
    indLangs = lang.split('-')
    isoCodeLangPair = '-'.join(list(map(toAlpha3Code, indLangs)))
    url = statsURL % isoCodeLangPair
    rawStats = s.post(url).json()
    if 'stats' in rawStats:
        return rawStats['stats']
    logging.error('Unable to request stats for %s' % isoCodeLangPair)

def getRevisionInfo(lang):
    try:
        commitUrl = "https://api.github.com/repos/apertium/apertium-%/commits" % lang
        commitsJson = s.get(url).json()
        revisionNumber = commitsJson[0]['sha']
        revisionAuthor = commitsJson[0]['committer']['date']
        return (revisionNumber, revisionAuthor)
    except Exception as e:
        logging.error('Unable to get revision info for %s: %s' % (uri, e))

def createStatsSection(fileCounts, requester=None):
    statsSection = '==Over-all stats=='
    for countName in sorted(fileCounts.keys(), key=lambda countName: (fileCounts[countName] and fileCounts[countName][0] is 0, countName)):
        if fileCounts[countName]:
            count, revisionInfo, fileUrl = fileCounts[countName]
            statsSection += '\n' + createStatSection(countName, count, revisionInfo, fileUrl, requester=requester)
        else:
            statsSection += "\n*'''{0}''': <section begin={1} />?<section end={1} /> ~ ~~~~".format(countName, countName.replace(' ', '_'))
            if requester:
                statsSection += ', run by %s' % requester
    return statsSection

def createStatSection(countName, count, revisionInfo, fileUrl, requester=None):
    if count is 0:
        statSection = "*<span style='opacity: .6'>'''[{6} {0}]''': <section begin={1} />{2:,d}<section end={1} /> as of [{3} {5}] by {4} ~ ~~~~".format(countName, countName.replace(' ', '_'), count, revisionInfo[0], revisionInfo[1], revisionInfo[2], fileUrl)
    else:
        statSection = "*'''[{6} {0}]''': <section begin={1} />{2}<section end={1} /> as of [{3} {5}] by {4} ~ ~~~~".format(countName, countName.replace(' ', '_'), count, revisionInfo[0], revisionInfo[1], revisionInfo[2], fileUrl)

    if requester:
        statSection += ', run by %s' % requester

    if count is 0:
        statSection += '</span>'

    return statSection

def updatePairStatsSection(statsSection, pageContents, fileCounts, requester=None):
    matchAttempts = re.finditer(r'(^\*.*?<section begin=([^/]+)/>.*?$)', pageContents, re.MULTILINE)
    replacements = {}
    for matchAttempt in matchAttempts:
        countName = matchAttempt.group(2).strip().replace('_', ' ')
        if countName in fileCounts:
            count, revisionInfo, fileUrl = fileCounts[countName]
            replacement = createStatSection(countName, count, revisionInfo, fileUrl, requester=requester)
            replacements[(matchAttempt.group(1))] = replacement
            del fileCounts[countName]
            logging.debug('Replaced count %s' % repr(countName))
        else:
            langPairEndIndex = countName.find('-', countName.find('-') + 1)
            oldLangPairEntry = langPairEndIndex != -1 and countName[:langPairEndIndex] + countName[langPairEndIndex:].replace('-', ' ') in fileCounts
            oldLangEntry = countName.count('-') == 1 and countName.replace('-', ' ') in fileCounts
            postEntry = countName.startswith('post')
            if oldLangEntry or oldLangPairEntry or postEntry:
                replacements[(matchAttempt.group(1))] = ''
                logging.debug('Deleting old style count %s' % repr(countName))

    for old, new in replacements.items():
        if new == '':
            pageContents = pageContents.replace(old + '\n', new)
        pageContents = pageContents.replace(old, new)

    newStats = ''
    for countName in sorted(fileCounts.keys(), key=lambda countName: (fileCounts[countName] and fileCounts[countName][0] is 0, countName)):
        if fileCounts[countName]:
            count, revisionInfo, fileUrl = fileCounts[countName]
            newStats += '\n' + createStatSection(countName, count, revisionInfo, fileUrl, requester=requester)
        else:
            newStats += "\n*'''{0}''': <section begin={1} />?<section end={1} /> ~ ~~~~".format(countName, countName.replace(' ', '_'))
            if requester:
                newStats += ', run by %s' % requester
        logging.debug('Adding new count %s' % repr(countName))
    newStats += '\n'

    contentBeforeIndex = statsSection.start()
    contentAfterIndex = pageContents.find('==', statsSection.end() + 1) if pageContents.find('==', statsSection.end() + 1) != -1 else len(pageContents)
    pageContents = pageContents[:contentBeforeIndex] + pageContents[contentBeforeIndex:contentAfterIndex].rstrip() + newStats + '\n' + pageContents[contentAfterIndex:]

    return pageContents

def updateMonoLangStatsSection(statsSection, pageContents, fileCounts, requester=None):
    matchAttempts = re.finditer(r'(^\*.*?<section begin=([^/]+)/>.*?$)', pageContents, re.MULTILINE)
    replacements = {}
    for matchAttempt in matchAttempts:
        countName = matchAttempt.group(2).strip().replace('_', ' ')
        if countName in fileCounts:
            count, revisionInfo, fileUrl = fileCounts[countName]
            replacement = createStatSection(countName, count, revisionInfo, fileUrl, requester=args.requester)
            replacements[(matchAttempt.group(1))] = replacement
            del fileCounts[countName]
            logging.debug('Replaced count %s' % repr(countName))
    for old, new in replacements.items():
        pageContents = pageContents.replace(old, new)

    newStats = ''
    for countName in sorted(fileCounts.keys(), key=lambda countName: (fileCounts[countName] and fileCounts[countName][0] is 0, countName)):
        count, revisionInfo, fileUrl = fileCounts[countName]
        newStats += '\n' + createStatSection(countName, count, revisionInfo, fileUrl, requester=args.requester)
        logging.debug('Adding new count %s' % repr(countName))
    newStats += '\n'

    contentBeforeIndex = statsSection.start()
    contentAfterIndex = pageContents.find('==', statsSection.end() + 1) if pageContents.find('==', statsSection.end() + 1) != -1 else len(pageContents)
    pageContents = pageContents[:contentBeforeIndex] + pageContents[contentBeforeIndex:contentAfterIndex].rstrip() + newStats + '\n' + pageContents[contentAfterIndex:]

    return pageContents

def addCategory(pageContents):
    categoryMarker = '[[Category:Datastats]]'
    if categoryMarker in pageContents:
        return pageContents
    else:
        logging.debug('Adding category marker (%s)' % categoryMarker)
        return pageContents + '\n' * 3 + categoryMarker

def toISO(code):
    iso639Codes = {"abk":"ab","aar":"aa","afr":"af","aka":"ak","sqi":"sq","amh":"am","ara":"ar","arg":"an","hye":"hy","asm":"as","ava":"av","ave":"ae","aym":"ay","aze":"az","bam":"bm","bak":"ba","eus":"eu","bel":"be","ben":"bn","bih":"bh","bis":"bi","bos":"bs","bre":"br","bul":"bg","mya":"my","cat":"ca","cha":"ch","che":"ce","nya":"ny","zho":"zh","chv":"cv","cor":"kw","cos":"co","cre":"cr","hrv":"hr","ces":"cs","dan":"da","div":"dv","nld":"nl","dzo":"dz","eng":"en","epo":"eo","est":"et","ewe":"ee","fao":"fo","fij":"fj","fin":"fi","fra":"fr","ful":"ff","glg":"gl","kat":"ka","deu":"de","ell":"el","grn":"gn","guj":"gu","hat":"ht","hau":"ha","heb":"he","her":"hz","hin":"hi","hmo":"ho","hun":"hu","ina":"ia","ind":"id","ile":"ie","gle":"ga","ibo":"ig","ipk":"ik","ido":"io","isl":"is","ita":"it","iku":"iu","jpn":"ja","jav":"jv","kal":"kl","kan":"kn","kau":"kr","kas":"ks","kaz":"kk","khm":"km","kik":"ki","kin":"rw","kir":"ky","kom":"kv","kon":"kg","kor":"ko","kur":"ku","kua":"kj","lat":"la","ltz":"lb","lug":"lg","lim":"li","lin":"ln","lao":"lo","lit":"lt","lub":"lu","lav":"lv","glv":"gv","mkd":"mk","mlg":"mg","msa":"ms","mal":"ml","mlt":"mt","mri":"mi","mar":"mr","mah":"mh","mon":"mn","nau":"na","nav":"nv","nob":"nb","nde":"nd","nep":"ne","ndo":"ng","nno":"nn","nor":"no","iii":"ii","nbl":"nr","oci":"oc","oji":"oj","chu":"cu","orm":"om","ori":"or","oss":"os","pan":"pa","pli":"pi","fas":"fa","pol":"pl","pus":"ps","por":"pt","que":"qu","roh":"rm","run":"rn","ron":"ro","rus":"ru","san":"sa","srd":"sc","snd":"sd","sme":"se","smo":"sm","sag":"sg","srp":"sr","gla":"gd","sna":"sn","sin":"si","slk":"sk","slv":"sl","som":"so","sot":"st","azb":"az","spa":"es","sun":"su","swa":"sw","ssw":"ss","swe":"sv","tam":"ta","tel":"te","tgk":"tg","tha":"th","tir":"ti","bod":"bo","tuk":"tk","tgl":"tl","tsn":"tn","ton":"to","tur":"tr","tso":"ts","tat":"tt","twi":"tw","tah":"ty","uig":"ug","ukr":"uk","urd":"ur","uzb":"uz","ven":"ve","vie":"vi","vol":"vo","wln":"wa","cym":"cy","wol":"wo","fry":"fy","xho":"xh","yid":"yi","yor":"yo","zha":"za","zul":"zu", "hbs":"sh", "arg":"an", "pes":"fa"}
    if code in iso639Codes:
        return iso639Codes[code]
    else:
        return code

def toAlpha3Code(code):
    iso639Codes = {"abk":"ab","aar":"aa","afr":"af","aka":"ak","sqi":"sq","amh":"am","ara":"ar","arg":"an","hye":"hy","asm":"as","ava":"av","ave":"ae","aym":"ay","aze":"az","bam":"bm","bak":"ba","eus":"eu","bel":"be","ben":"bn","bih":"bh","bis":"bi","bos":"bs","bre":"br","bul":"bg","mya":"my","cat":"ca","cha":"ch","che":"ce","nya":"ny","zho":"zh","chv":"cv","cor":"kw","cos":"co","cre":"cr","hrv":"hr","ces":"cs","dan":"da","div":"dv","nld":"nl","dzo":"dz","eng":"en","epo":"eo","est":"et","ewe":"ee","fao":"fo","fij":"fj","fin":"fi","fra":"fr","ful":"ff","glg":"gl","kat":"ka","deu":"de","ell":"el","grn":"gn","guj":"gu","hat":"ht","hau":"ha","heb":"he","her":"hz","hin":"hi","hmo":"ho","hun":"hu","ina":"ia","ind":"id","ile":"ie","gle":"ga","ibo":"ig","ipk":"ik","ido":"io","isl":"is","ita":"it","iku":"iu","jpn":"ja","jav":"jv","kal":"kl","kan":"kn","kau":"kr","kas":"ks","kaz":"kk","khm":"km","kik":"ki","kin":"rw","kir":"ky","kom":"kv","kon":"kg","kor":"ko","kur":"ku","kua":"kj","lat":"la","ltz":"lb","lug":"lg","lim":"li","lin":"ln","lao":"lo","lit":"lt","lub":"lu","lav":"lv","glv":"gv","mkd":"mk","mlg":"mg","msa":"ms","mal":"ml","mlt":"mt","mri":"mi","mar":"mr","mah":"mh","mon":"mn","nau":"na","nav":"nv","nob":"nb","nde":"nd","nep":"ne","ndo":"ng","nno":"nn","nor":"no","iii":"ii","nbl":"nr","oci":"oc","oji":"oj","chu":"cu","orm":"om","ori":"or","oss":"os","pan":"pa","pli":"pi","fas":"fa","pol":"pl","pus":"ps","por":"pt","que":"qu","roh":"rm","run":"rn","ron":"ro","rus":"ru","san":"sa","srd":"sc","snd":"sd","sme":"se","smo":"sm","sag":"sg","srp":"sr","gla":"gd","sna":"sn","sin":"si","slk":"sk","slv":"sl","som":"so","sot":"st","azb":"az","spa":"es","sun":"su","swa":"sw","ssw":"ss","swe":"sv","tam":"ta","tel":"te","tgk":"tg","tha":"th","tir":"ti","bod":"bo","tuk":"tk","tgl":"tl","tsn":"tn","ton":"to","tur":"tr","tso":"ts","tat":"tt","twi":"tw","tah":"ty","uig":"ug","ukr":"uk","urd":"ur","uzb":"uz","ven":"ve","vie":"vi","vol":"vo","wln":"wa","cym":"cy","wol":"wo","fry":"fy","xho":"xh","yid":"yi","yor":"yo","zha":"za","zul":"zu", "hbs":"sh", "arg":"an", "pes":"fa"}
    '''
        Bootstrapped from https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes using
            var out = {};
            $.each($('tr', $('table').get(1)), function(i, elem) { var rows = $('td', elem); out[$(rows[5]).text()] = $(rows[4]).text(); });
            JSON.stringify(out);
    '''

    iso639CodesInverse = {v: k for k, v in iso639Codes.items()}
    if '_' in code:
        code, variant = code.split('_')
        return '%s_%s' % ((iso639CodesInverse[code], variant) if code in iso639CodesInverse else  (code, variant))
    else:
        return iso639CodesInverse[code] if code in iso639CodesInverse else code

def getPage(pageTitle):
    payload = {'action': 'query', 'format': 'json', 'titles': pageTitle, 'prop': 'revisions', 'rvprop': 'content'}
    viewResult = s.get(apiURL, params=payload)
    jsonResult = json.loads(viewResult.text)

    if not 'missing' in list(jsonResult['query']['pages'].values())[0]:
        return list(jsonResult['query']['pages'].values())[0]['revisions'][0]['*']

def editPage(pageTitle, pageContents, editToken):
    payload = {'action': 'edit', 'format': 'json', 'title': pageTitle, 'text': pageContents, 'bot': 'True', 'contentmodel': 'wikitext', 'token': editToken}
    editResult = s.post(apiURL, data=payload)
    jsonResult = json.loads(editResult.text)
    return jsonResult

def login(loginName, password):
    try:
        payload = {'action': 'login', 'format': 'json', 'lgname': loginName, 'lgpassword': password}
        authResult = s.post(apiURL, params=payload)
        authToken = json.loads(authResult.text)['login']['token']
        logging.debug('Auth token: %s' % authToken)

        payload = {'action': 'login', 'format': 'json', 'lgname': loginName, 'lgpassword': password, 'lgtoken': authToken}
        authResult = s.post(apiURL, params=payload)
        if not json.loads(authResult.text)['login']['result'] == 'Success':
            logging.critical('Failed to login as %s: %s' % (loginName, json.loads(authResult.text)['login']['result']))
        else:
            logging.info('Login as %s succeeded' % loginName)
            return authToken
    except Exception as e:
        logging.critical('Failed to login: %s' % e)

def human_format(num):
    num = float('{:.2g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def addCorporaSection(pageContents):
    pageContents.replace('[[Category:Datastats]]\n', '').replace('[[Category:Datastats]]', '')
    pageContents += '\n== Corpora ==\n'
    pageContents += '[[Category:Datastats]]'
    return pageContents

def updateCoverageStats(pageContents, coverage, words, lang):
    newPageContents = ''

    templateLine = re.compile('==\s*.*\s*==')
    wpName = 'wp%s' % datetime.datetime.now().year

    isCorpora = False
    isAfter = False

    beforeSection = ''
    newMiddleSection = ''
    middleSection = ''
    afterSection = ''

    lines = pageContents.split('\n')

    wpExists = re.search(wpName+'\n', pageContents, re.IGNORECASE)

    for line in lines:
        if isCorpora:
            middleSection += line + '\n'
        elif isAfter:
            afterSection += line + '\n'
        else:
            beforeSection += line + '\n'

        if templateLine.match(line):
            if 'Corpora' in line:
                isCorpora = True
        elif line.startswith(wpName):
            isAfter = True
        elif isCorpora and isAfter and line == '':
            isCorpora = False
    words, coverage, revisionNum = human_format(words), '{0:.1f}'.format(coverage), getRevisionInfo(lang)
    middleSection = middleSection.replace('[[Category:Datastats]]\n', '').replace('[[Category:Datastats]]', '')
    afterSection = afterSection.replace('[[Category:Datastats]]\n', '').replace('[[Category:Datastats]]', '')

    if not wpExists:
        while middleSection.endswith('\n'):
            middleSection = middleSection[:-2]
        middleSection += '\n\n' + wpName + '\n'
        middleSection += '* words: <section begin=' + wpName + '-words />' + words + '<section end=' + wpName + '-words />\n'
        middleSection += '* coverage: ~<section begin=' + wpName + '-coverage />' + coverage + '<section end=' + wpName + '-coverage />%\n'
        middleSection += '* as of: ' + revisionNum[0] + '\n'
    else:
        wpSection = ''
        wpSection += wpName + '\n'
        wpSection += '* words: <section begin=' + wpName + '-words />' + words + '<section end=' + wpName + '-words />\n'
        wpSection += '* coverage: ~<section begin=' + wpName + '-coverage />' + coverage + '<section end=' + wpName + '-coverage />%\n'
        wpSection += '* as of: ' + revisionNum[0] + '\n'

        middleSection = middleSection[:middleSection.index(wpName+'\n')] + wpSection + middleSection[len(middleSection)-1]

    afterSection += '[[Category:Datastats]]'
    newPageContents = beforeSection + middleSection + afterSection
    return newPageContents

def getToken(tokenType, props):
    try:
        payload = {'action': 'query', 'format': 'json', 'prop': props, 'intoken': tokenType, 'titles':'Main Page'}
        tokenResult = s.get(apiURL, params=payload)
        token = json.loads(tokenResult.text)['query']['pages']['1']['%stoken' % tokenType]
        logging.debug('%s token: %s' % (tokenType, token))
        return token
    except Exception as e:
        logging.error('Failed to obtain %s token: %s' % (tokenType, e))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Apertium Wiki Bot")
    parser.add_argument('loginName', help="bot login name")
    parser.add_argument('password', help="bot password")
    parser.add_argument('action', help="action for bot to perform", choices=['dict', 'coverage'])
    parser.add_argument('-p', '--pairs', nargs='+', help="Apertium language pairs/monolingual packages in the format e.g. bg-ru or rus")
    parser.add_argument('-a', '--analyzers', nargs='+', help="Apertium analyzers (.automorf.bin files)")
    parser.add_argument('-v', '--verbose', help="verbose mode (debug)", action='store_true', default=False)
    parser.add_argument('-r', '--requester', help="user who requests update", default=None)

    args = parser.parse_args()
    if args.action == 'dict' and not args.pairs:
        parser.error('action "dict" requires pairs (-p, --pairs) argument')
    if args.action == 'coverage':
        if not args.pairs:
            parser.error('action "coverage" requires pairs (-p, --pairs) argument')

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    authToken = login(args.loginName, args.password)
    moveToken = getToken('move', 'info')
    editToken = getToken('edit', 'info|revisions')
    if not all([authToken, moveToken, editToken]):
        logging.critical('Failed to obtain required token')
        sys.exit(-1)

    if args.action == 'dict':
        for pair in args.pairs:
            try:
                langs = pair.split('-')
                pageTitle = 'Apertium-' + '-'.join(langs) + '/stats'
                if len(langs) == 2 and not(getPage(pageTitle)):
                    langs = list(map(toISO, langs))
                if len(langs) == 1:
                    pageTitle = 'Apertium-' + toAlpha3Code(langs[0]) + '/stats'
            except:
                logging.error('Failed to parse language module name: %s' % pair)
                break
            jsonResponse = getJSONFromStatsService(pair)
            if len(langs) == 2:
                fileCounts = getStats(jsonResponse, False)
                logging.debug('Acquired file counts %s' % fileCounts)

                if len(fileCounts) is 0:
                    logging.error('No file counts available for %s, adding placeholder bidix stems entry.' % repr(langs))
                    fileCounts = {'%s-%s stems' % tuple(langs): None}

                pageContents = getPage(pageTitle)
                if pageContents:
                    statsSection = re.search(r'==\s*Over-all stats\s*==', pageContents, re.IGNORECASE)
                    if statsSection:
                        pageContents = updatePairStatsSection(statsSection, pageContents, fileCounts, requester=args.requester)
                    else:
                        pageContents += '\n' + createStatsSection(fileCounts, requester=args.requester)
                        logging.debug('Adding new stats section')

                    pageContents = addCategory(pageContents)
                    editResult = editPage(pageTitle, pageContents, editToken)
                    if editResult['edit']['result'] == 'Success':
                        logging.info('Update of page {0} succeeded ({1}{0})'.format(pageTitle, wikiURL))
                    else:
                        logging.error('Update of page %s failed: %s' % (pageTitle, editResult))
                else:
                    pageContents = createStatsSection(fileCounts, requester=args.requester)
                    pageContents = addCategory(pageContents)

                    editResult = editPage(pageTitle, pageContents, editToken)
                    if editResult['edit']['result'] == 'Success':
                        logging.info('Creation of page {0} succeeded ({1}{0})'.format(pageTitle, wikiURL))
                    else:
                        logging.error('Creation of page %s failed: %s' % (pageTitle, editResult.text))

            elif len(langs) == 1:
                fileCounts = getStats(jsonResponse, True)
                logging.info('Acquired file counts %s' % fileCounts)
                if fileCounts:
                    pageContents = getPage(pageTitle)
                    if pageContents:
                        statsSection = re.search(r'==\s*Over-all stats\s*==', pageContents, re.IGNORECASE)
                        if statsSection:
                            pageContents = updateMonoLangStatsSection(statsSection, pageContents, fileCounts, requester=args.requester)
                        else:
                            pageContents += '\n' + createStatsSection(fileCounts, requester=args.requester)
                            logging.debug('Adding new stats section')

                        pageContents = addCategory(pageContents)
                        editResult = editPage(pageTitle, pageContents, editToken)
                        if editResult['edit']['result'] == 'Success':
                            logging.info('Update of page {0} succeeded ({1}{0})'.format(pageTitle, wikiURL))
                        else:
                            logging.error('Update of page %s failed: %s' % (pageTitle, editResult))
                    else:
                        pageContents = createStatsSection(fileCounts, requester=args.requester)
                        pageContents = addCategory(pageContents)

                        editResult = editPage(pageTitle, pageContents, editToken)
                        if editResult['edit']['result'] == 'Success':
                            logging.info('Creation of page {0} succeeded ({1}{0})'.format(pageTitle, wikiURL))
                        else:
                            logging.error('Creation of page %s failed: %s' % (pageTitle, editResult.text))
                else:
                    logging.error('No file counts available for %s, skipping.' % repr(langs))
            else:
                logging.error('Invalid language module name: %s' % pair)
    elif args.action == 'coverage':
        lang = args.pairs[0]
        wikiPath, coverage = autocoverage.StartScript(False, False, '', lang)
        words = autocoverage.CountWords(wikiPath)
        pageTitle = 'Apertium-' + lang + '/stats'
        pageContents = getPage(pageTitle)

        if pageContents:

            corporaSection = re.search(r'==\s*Corpora\s*==', pageContents, re.IGNORECASE)
            if corporaSection:
                pageContents = updateCoverageStats(pageContents, coverage, words, lang)
                editPage(pageTitle, pageContents, editToken)
            else:
                pageContents = addCorporaSection(pageContents)
                pageContents = updateCoverageStats(pageContents, coverage, words, lang)
                editPage(pageTitle, pageContents, editToken)
            shutil.rmtree('apertium-' + lang, ignore_errors=True)
        else:
            logging.error('Error, no content for this website!')
