'''
covid.py - Phenny Coronavirus Module
'''

import web
def scrape_stats(url):
    @web.with_scraped_page_no_cache(url)
    def scrape_stats_sub(doc):
        elements = doc.find_class('maincounter-number')
        try:
            heading = doc.find('h1').text_content().strip()
        except AttributeError:
            heading = 'the world'
        if heading == 'Coronavirus Cases:': #on the global stats page, the first h1 is just a data heading
            heading == 'the world'
        return tuple(( i.text_content().strip() for i in elements )) + ( heading, )
    return scrape_stats_sub()

def covid(phenny, input):
    '''.covid [country]: COVID-19 statistics; omit [country] for global stats (if country == 'us', you can specify a state after it)'''
    if input.group(1):
        country = input.group(1).split()[0]
        if country.lower() == 'usa':
            country == 'us'
        if country.lower() == 'georgia':
            phenny.say('Note: this information is for the country of Georgia. US states are not supported.')
        #try:
        #    state = input.group(1).split()[1]
        #except IndexError:
        #    state = None
        #if country.lower() == 'us' and state:
        #    url = 'https://www.worldometers.info/coronavirus/usa/{}'.format(state)
        #else:
        url = 'https://www.worldometers.info/coronavirus/country/{}'.format(country)
    else:
        url = 'https://www.worldometers.info/coronavirus/'
    
    try:
        cases, deaths, recovered, place = scrape_stats(url)
    except ValueiError:
        if 'country' in locals():
            phenny.say('Sorry, an error occurred. If there is another name for {}, try it.'.format(state if state else country))
        else:
            phenny.say('Sorry, an error occurred.')
        return
    except Exception as e:
        phenny.say('Sorry, an error occurred.')
        raise e
    try:
        int(deaths.replace(',', ''))
    except ValueError:
        deaths = '10,000,000,000' #more than the world population; this will never be real data
    try:
        int(recovered.replace(',', ''))
    except ValueError:
        recovered = '10,000,000,000'
    try:
        int(cases.replace(',', ''))
    except ValueError:
       cases  = '10,000,000,000'
    current = format(int(cases.replace(',', '')) - ( int(deaths.replace(',', '')) + int(recovered.replace(',', '')) ), ',d')
    outcome = format(int(deaths.replace(',', '')) + int(recovered.replace(',', '')), ',d')
    phenny.say('{}here have been {} cases of COVID-19, including {} with an outcome ({} recoveries and {} deaths), leaving {} current cases. There have been {} recoveries for every 1 death. This is not medical advice. Source: {}'.format(
        'T' if place == 'the world' else 'In {}, t'.format(place),
        '<unknown>' if cases == '10,000,000,000' else cases,
        '<unknown>' if '10,000,000,000' in (recovered, deaths) else outcome,
        '<unknown>' if recovered == '10,000,000,000' else recovered,
        '<unknown>' if deaths == '10,000,000,000' else deaths,
        '<unknown>' if '10,000,000,000' in (cases, recovered, deaths) else current,
        '<unknown>' if '10,000,000,000' in (cases, recovered, deaths) else round(int(recovered.replace(',', ''))/int(deaths.replace(',', '')) * 100 ) / 100, url ))
covid.commands = ['covid', 'covid19', 'coronavirus', '2019ncov', 'sarscov2', 'corona', 'pandemic']
covid.example = '.covid uk'
covid.priority = 'medium'
