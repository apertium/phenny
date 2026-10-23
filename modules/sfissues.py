import feedparser
from bot import keyword

def get_headlines(rss_url):
    tickets = []
    feed = feedparser.parse(rss_url)
    for ticket_item in feed['items']:
        tickets.append(ticket_item['title'])
    return tickets

@keyword('.*bugs!.*')
def bugs(phenny, msg):
    if phenny.nick not in msg.text:
        return
    messages = []
    rep_messages = []
    url = phenny.config.sf_issues_url
    messages.extend(get_headlines(url))
    for items in messages:
        if items[0] != '#':
            rep_messages.append(items)
    phenny.say('{}: {}'.format(msg.nick, ', '.join(rep_messages)))
