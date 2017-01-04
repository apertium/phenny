#!/usr/bin/python3
"""
8ball.py - magic 8-ball
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import random
STRONG_YES = [
            '45 seconds full throttle',
            'It is certain',
            'It is decidedly so',
            'Without a doubt',
            'Yes--definitely',
            'You may rely on it',
    ]
TENTATIVE_YES = [
            'As I see it, yes',
            'Most likely',
            'Outlook good',
            'Signs point to yes',
            'Yes',
    ]
NEGATIVE = [
            'Your request is not bro enough',
            'Reply hazy, try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
    ]
NONCOMMITAL = [
            'I am sorry, too high to respond',
            "Don't count on it",
            'My reply is no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful'
    ]

QUOTES = STRONG_YES + TENTATIVE_YES + NEGATIVE + NONCOMMITAL

def eightball(phenny, input):
    """.8ball - Magic 8-ball."""


    # black magic
    quote = random.choice(QUOTES)
    phenny.reply(quote)
eightball.commands = ['8ball']
eightball.name = '8ball'
eightball.example = '.8ball is begiak amazing?'

if __name__ == '__main__':
    print(__doc__.strip())
