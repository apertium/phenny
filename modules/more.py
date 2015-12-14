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
        parts.append(string[:max_length-3] + '...')
        string = string[max_length-3:]
    parts.append(string)
    return parts

def add_messages(target, phenny, msg, break_up=break_up_fn):
    max_length = 428 - len(target)
    msgs = break_up(str(msg), max_length)
    phenny.say(target + ': ' + msgs[0])
    if len(msgs) > 1:
        phenny.say(target + ': you have more messages. Please ".more" to view them.')
        msgs = msgs[1:]
        if target in phenny.messages.keys():
            for m in msgs:
                phenny.messages[target].append(m)
        else:
            phenny.messages[target] = msgs

def more(phenny, input):
    if input.nick in phenny.messages.keys():
        phenny.say(input.nick + ': ' + phenny.messages[input.nick][0])
        if len(phenny.messages[input.nick]) == 1:
            del phenny.messages[input.nick]
        else:
            phenny.messages[input.nick].remove(phenny.messages[input.nick][0])
    else:
        phenny.say(input.nick + ': you do not have any pending messages.')
more.name = 'more'
more.rule = r'[.]more'
