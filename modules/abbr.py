#!/usr/bin/python3

abbrs = {
    "lol": "laugh out loud",
    "omg": "oh my gosh",
    "rofl": "rolling on the floor laughing",
    "nn": "neural network; night nigh",
    "roflol": "rolling on the floor laughing out loud",
    "brb": "be right back",
    "bbif": "be back in a few",
    "bbf": "be back in a few",
    "kk": "ok",
    "pls": "please",
    "plz": "please",
    "witw": "what in the world",
    "nvm": "never mind",
    "idk": "i don't know",
    "asap": "as soon as possible",
    "btw": "by the way",
    "gtg": "got to go",
    "pm": "private message",
    "dm": "direct message",
    "jk": "just kidding",
    "np": "no problem",
    "msg": "message",
    "thx": "thanks",
    "ty": "thank you",
    "nty": "no thank you",
    "fyi": "for your information"
}

from bot import command

@command('abbr', ping=False, example='.abbr lol')
def abbr(phenny, msg):
    '''.abbr <abbreviation> - search for meaning of abbreviation '''
    if not msg.command_args:
        return 'usage: .abbr <query>'
    elif msg.command_args in abbrs:
        return '{} means "{}"'.format(msg.command_args,
                                      abbrs[msg.command_args])
    else:
        return "I'm not sure what {} means.".format(msg.command_args)
