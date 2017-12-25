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
    caseless_nick = target.casefold()

    if not target in phenny.config.channels:
        msgs = list(map(lambda msg: target + ': ' + msg, msgs))

    if len(msgs) <= 2:
        for msg in msgs:
            phenny.msg(target, msg)
    else:
        phenny.msg(target, msgs[0])
        msgs = msgs[1:]
        phenny.msg(target, 'you have ' + str(len(msgs)) + ' more message(s). Please type ".more" to view them.')
        phenny.messages[caseless_nick] = msgs

def more(phenny, input):
    caseless_nick = input.nick.casefold()

    if caseless_nick in phenny.messages.keys():
        show_more(phenny, caseless_nick)
    elif input.admin or input.owner:
        caseless_sender = input.sender.casefold()

        if caseless_sender in phenny.messages.keys():
            show_more(phenny, caseless_sender)

more.name = 'more'
more.rule = r'[.]more'

def show_more(phenny, caseless_nick):
    msg = phenny.messages[caseless_nick][0]
    phenny.messages[caseless_nick].remove(phenny.messages[caseless_nick][0])
    remaining = ' (' + str(len(phenny.messages[caseless_nick])) + ')' if phenny.messages[caseless_nick] else ''
    phenny.reply(msg + remaining)

    if not phenny.messages[caseless_nick]:
        del phenny.messages[caseless_nick]
