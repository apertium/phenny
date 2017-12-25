#!usr/bin/python3
"""
more.py - Message Buffer Interface
Author - mandarj
"""

def setup(self):
    self.messages = {}

def break_up_fn(string, max_length):
    parts = []

    while len(string) > max_length:
        tmp = string[:max_length]

        if ' ' in tmp[-4:]:
            tmp = string[:max_length-4] # or else no space for ' ...'

        while not tmp[-1] == ' ':
            tmp = tmp[:-1]

        string = string[len(tmp):] # also skips space at the end of tmp
        parts.append(tmp.strip() + ' ...')

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
        phenny.msg(target, msgs.pop(0))
        phenny.msg(target, 'you have ' + str(len(msgs)) + ' more message(s). Please type ".more" to view them.')
        phenny.messages[caseless_nick] = msgs

def more(phenny, input):
    ''' '.more N' prints the next N messages.
        If N is not specified, prints the next message.'''

    count = 1 if input.group(1) is None else int(input.group(1))

    if has_more(phenny, input.nick):
        show_more(phenny, input.nick, count)
    elif (input.admin or input.owner) and has_more(phenny, input.sender):
        show_more(phenny, input.sender, count)
    else:
        phenny.reply("No more queued messages")

more.name = 'more'
more.rule = r'[.]more(?: ([1-9][0-9]*))?'

def has_more(phenny, nick):
    return nick.casefold() in phenny.messages.keys()

def show_more(phenny, nick, count):
    caseless_nick = nick.casefold()
    remaining = len(phenny.messages[caseless_nick])

    if count > remaining:
        count = remaining

    remaining -= count

    if count > 1:
        for _ in range(count):
            phenny.reply(phenny.messages[caseless_nick].pop(0))

        if remaining > 0:
            phenny.reply(str(remaining) + " message(s) remaining")
    else:
        msg = phenny.messages[caseless_nick].pop(0)

        if remaining > 0:
            phenny.reply(msg + " (" + str(remaining) + " remaining)")
        else:
            phenny.reply(msg)

    if remaining == 0:
        del phenny.messages[caseless_nick]
