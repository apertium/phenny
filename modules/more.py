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
    max_length = 428 - len(target) - 5
    msgs = break_up(str(msg), max_length)
    lowernick = target.casefold();

    if len(msgs) <= 2:
        for msg in msgs:
            phenny.reply(msg)
    else:
        phenny.reply(msgs[0])
        msgs = msgs[1:]
        phenny.reply('you have ' + str(len(msgs)) + ' more message(s). Please type ".more" to view them.')
        phenny.messages[lowernick] = msgs

def more(phenny, input):
    lowernick = input.nick.casefold();

    if lowernick in phenny.messages.keys():
        msg = phenny.messages[lowernick][0]
        phenny.messages[lowernick].remove(phenny.messages[lowernick][0])
        remaining = ' (' + str(len(phenny.messages[lowernick])) + ')' if phenny.messages[lowernick] else ''
        phenny.reply(msg + remaining)
        if not phenny.messages[lowernick]:
            del phenny.messages[lowernick]

more.name = 'more'
more.rule = r'[.]more'