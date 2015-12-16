#!usr/bin/python3
"""
more.py - Message Buffer Interface
Author - mandarj
"""

def setup(self):
    self.messages = {}

def break_up_fn(string, max_length):
    parts = []
    tmp = ''
    while len(string) > max_length:
        tmp = string[:max_length]
        if ' ' in tmp[-3:]:
            tmp = string[:max_length-3] # or else no space for '...'
        while not tmp[-1] == ' ':
            tmp = tmp[:-1]
        string = string[len(tmp):] # also skips space at the end of tmp
        parts.append(tmp.strip() + '...')
        tmp = ''

    parts.append(string)
    return parts

def add_messages(target, phenny, msg, break_up=break_up_fn):
    max_length = 428 - len(target) - 5
    msgs = break_up(str(msg), max_length)
    phenny.say(target + ': ' + msgs[0])
    
    if len(msgs) > 1:
        msgs = msgs[1:]
        phenny.say(target + ': you have ' + str(len(msgs)) + ' more messages. Please ".more" to view them.')
        phenny.messages[target] = msgs

def more(phenny, input):
    if input.nick in phenny.messages.keys():
        msg = phenny.messages[input.nick][0]
        phenny.messages[input.nick].remove(phenny.messages[input.nick][0])
        remaining = ' (' + str(len(phenny.messages[input.nick])) + ')' if phenny.messages[input.nick] else ''
        phenny.say(input.nick + ': ' + msg + remaining)
        if not phenny.messages[input.nick]:
            del phenny.messages[input.nick]
    else:
        phenny.say(input.nick + ': you do not have any pending messages.')
more.name = 'more'
more.rule = r'[.]more'
