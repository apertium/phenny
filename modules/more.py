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
        if ' ' in tmp[-4:]:
            tmp = string[:max_length-4] # or else no space for ' ...'
        while not tmp[-1] == ' ':
            tmp = tmp[:-1]
        string = string[len(tmp):] # also skips space at the end of tmp
        parts.append(tmp.strip() + ' ...')
        tmp = ''

    parts.append(string)
    return parts

def add_messages(target, phenny, msg, break_up=break_up_fn):
    max_length = (config.maxlength - 2) - len(target) - 5
    msgs = break_up(str(msg), max_length)

    if len(msgs) <= 2:
        for msg in msgs:
            phenny.reply(msg)
    else:
        phenny.reply(msgs[0])
        msgs = msgs[1:]
        phenny.reply('you have ' + str(len(msgs)) + ' more message(s). Please type ".more" to view them.')
        phenny.messages[target] = msgs

def more(phenny, input):
    if input.nick in phenny.messages.keys():
        msg = phenny.messages[input.nick][0]
        phenny.messages[input.nick].remove(phenny.messages[input.nick][0])
        remaining = ' (' + str(len(phenny.messages[input.nick])) + ')' if phenny.messages[input.nick] else ''
        phenny.reply(msg + remaining)
        if not phenny.messages[input.nick]:
            del phenny.messages[input.nick]

more.name = 'more'
more.rule = r'[.]more'
