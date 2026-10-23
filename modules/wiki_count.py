"""
.wikicount <lg> - return the number of wikipedia articles in lg's wiki
author: mattr555
"""

from lxml import html
import web
from bot import command

def scrape_wiki_list():
    data = {}
    url = 'https://meta.wikimedia.org/wiki/List_of_Wikipedias'
    resp = web.get(url)
    h = html.document_fromstring(resp)
    for e in h.find_class('sortable'):
        for row in e.findall('tr')[1:]:
            name = row.findall('td')[1].find('a').text
            code = row.findall('td')[3].find('a').text
            count = int(row.findall('td')[4].find('a/b').text.replace(',', ''))
            data[code] = (name, count)
    return data

def scrape_incubator_list():
    data = {}
    url = 'https://incubator.wikimedia.org/wiki/Template:Tests/wp'
    resp = web.get(url)
    h = html.document_fromstring(resp)
    for row in h.find_class('wikitable')[0].findall('tr')[2:]:
        #raw_name = row.findall('td')[0].find('a/b')
        raw_name = row.findall('td')[0].find('*/a/b').text
        #print(raw_name)
        name = ' '.join(raw_name.split(' ')[1:])
        raw_name2 = row.findall('td')[1].text
        if raw_name2 is not None:
            name += " ("+raw_name2+")"
        #print(name)
        #code = row.findall('td')[1].find('a').text.split(' ')[0][3:]
        code = row.findall('td')[0].findall('*/a')[-1].text.split('/')[1]
        #print(code)
        data[code] = (name, None)
    return data

def scrape_iso_3to1(d):
    mapping = {}
    resp = web.get('https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes')
    h = html.document_fromstring(resp)
    table = h.find_class('wikitable')[0]
    for row in table.findall('tr')[1:]:
        try:
            three_code = row.findall('td')[7].text.split(' ')[0]
            one_code = row.findall('td')[4].text
            if one_code in d:
                mapping[three_code] = one_code
        except:
            pass
    return mapping

def wiki_response(info, lg):
    if info[1] is not None:
        url = 'https://{}.wikipedia.org/'.format(lg)
        response = 'The {} ({}) Wikipedia has {:,} articles. {}'.format(
            info[0], lg, info[1], url)
    else:
        url = 'https://incubator.wikimedia.org/wiki/Wp/' + lg
        resp = web.get('https://incubator.wikimedia.org/wiki/Template:Wp/{}/NUMBEROFARTICLES'.format(lg))
        num_articles = int(html.document_fromstring(resp).get_element_by_id('mw-content-text').find('*/p/a').text.replace(',', ''))
        response = 'The {} ({}) Wikipedia is incubated and has {:,} articles. {}'.format(
            info[0], lg, num_articles, url)
    return response

def update_article_count(phenny):
    phenny.wiki_data = scrape_incubator_list()
    phenny.wiki_data.update(scrape_wiki_list())

@command('wikicount', example='.wikicount en')
def wikicount(phenny, msg):
    lg = msg.command_args.lower()
    if lg == "update":
        if msg.admin:
            update_article_count(phenny)
            phenny.say('Wikipedia article counts successfully updated.')
        return
    elif lg in phenny.wiki_data:
        info = phenny.wiki_data[lg]
        response = wiki_response(info, lg)
    elif lg in phenny.wiki_iso_3_map:
        real_lg = phenny.wiki_iso_3_map[lg]
        info = phenny.wiki_data[real_lg]
        response = wiki_response(info, real_lg)
    else:
        possible = []
        for k, v in phenny.wiki_data.items():
            if lg in v[0].lower():
                possible.append((k,v))
        if len(possible) == 1:
            response = wiki_response(possible[0][1], possible[0][0])
        elif len(possible) == 0:
            response = "That wiki code wasn't found."
        else:
            did_you_mean = []
            for i in possible:
                if i[1][1] is not None:
                    did_you_mean.append('{} ({}, {:,} articles)'.format(i[1][0], i[0], i[1][1]))
                else:
                    did_you_mean.append('{} ({}, incubated)'.format(i[1][0], i[0]))
            response = "Did you mean: " + ', '.join(did_you_mean)

    phenny.say(response)

def setup(phenny):
    update_article_count(phenny)
    phenny.wiki_iso_3_map = scrape_iso_3to1(phenny.wiki_data)
    phenny.wiki_iso_3_map.update({
        'sgs': 'bat-smg',
        'roa': 'nrm',
        'vro': 'fiu-vro',
        'yue': 'zh-yue',
        'nan': 'zh-min-nan',
        'lzh': 'zh-classical',
        'be-tarask': 'be-x-old'
    })
