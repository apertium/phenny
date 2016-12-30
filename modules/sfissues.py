import feedparser
 
# Function to fetch the rss feed and return the parsed RSS
def parse_rss(rss_url):
    return feedparser.parse(rss_url) 
    
# Function grabs the rss feed headlines (titles) and returns them as a list
def getHeadlines(rss_url):
    tickets = []
    feed = parse_rss(rss_url)
    for ticketitem in feed['items']:
        tickets.append(ticketitem['title'])
    return tickets
 
# A list to hold all headlines
def bugs(phenny,input):
    messages = []
    rep_messages = []
    url = phenny.config.sf_issues_url 
    messages.extend( getHeadlines(url))
    for items in messages:
        if items[0] != '#':
            rep_messages.append(items)
    phenny.say('{}: {}'.format(input.nick, ', '.join(rep_messages)))

bugs.rule = ('$nick', 'bugs!')
