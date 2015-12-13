#!usr/bin/python3
"""
more.py - Message Buffer Interface
Author - mandarj
"""

def setup(self):
    self.messages = {}

def add_messages(target, msgs, phenny):
    if target in phenny.messages.keys():
        for msg in msgs:
            phenny.messages[target].append(msg)
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
