import feedparser
 
def get_headlines(rss_url):
    tickets = []
    feed = feedparser.parse(rss_url)
    for ticket_item in feed['items']:
        tickets.append(ticket_item['title'])
    return tickets
 
def bugs(phenny, input):
    messages = []
    rep_messages = []
    url = phenny.config.sf_issues_url 
    messages.extend(get_headlines(url))
    for items in messages:
        if items[0] != '#':
            rep_messages.append(items)
    phenny.say('{}: {}'.format(input.nick, ', '.join(rep_messages)))

bugs.rule = ('$nick', 'bugs!')
