#!usr/bin/python3
"""
more.py - Message Buffer Interface
Author - mandarj
"""

from tools import break_up

def setup(self):
    self.messages = {}

def add_messages(target, phenny, msgs):
    if not type(msgs) is list:
        msgs = [msgs]

    if not target in phenny.config.channels:
        msgs = list(map(lambda msg: target + ': ' + msg, msgs))

    msgs = sum(map(lambda msg: break_up(msg), msgs), [])

    if len(msgs) <= 2:
        for msg in msgs:
            phenny.msg(target, msg)
    else:
        phenny.msg(target, msgs.pop(0))
        phenny.msg(target, 'you have ' + str(len(msgs)) + ' more message(s). Please type ".more" to view them.')

        if target.casefold() in phenny.messages:
            phenny.messages[target.casefold()].extend(msgs)
        else:
            phenny.messages[target.casefold()] = msgs

def more(phenny, input):
    ''' '.more N' prints the next N messages.
        If N is not specified, prints the next message.'''

    count = 1 if input.group(1) is None else int(input.group(1))

    if has_more(phenny, input.nick):
        show_more(phenny, input.sender, input.nick, count)
    elif (input.admin or input.owner) and has_more(phenny, input.sender):
        show_more(phenny, input.sender, input.sender, count)
    else:
        phenny.reply("No more queued messages")

more.name = 'more'
more.rule = r'[.]more(?: ([1-9][0-9]*))?'

def has_more(phenny, target):
    return target.casefold() in phenny.messages.keys()

def show_more(phenny, sender, target, count):
    target = target.casefold()
    remaining = len(phenny.messages[target])

    if count > remaining:
        count = remaining

    remaining -= count

    if count > 1:
        for _ in range(count):
            phenny.msg(sender, phenny.messages[target].pop(0))

        if remaining > 0:
            phenny.msg(sender, str(remaining) + " message(s) remaining")
    else:
        msg = phenny.messages[target].pop(0)

        if remaining > 0:
            phenny.msg(sender, msg + " (" + str(remaining) + " remaining)")
        else:
            phenny.msg(sender, msg)

    if remaining == 0:
        del phenny.messages[target]
