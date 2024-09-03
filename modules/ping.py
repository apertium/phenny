#!/usr/bin/env python
"""
ping.py - Phenny Ping Module
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import random
import re
import os
from tools import db_path

# if emptyHellos is True, respond to anyone sending a greeting to no one
# if emptyHellos is False, don't respond unless addressed
emptyHellos = False


#temporaryMessage = "  If you're a GSoC student, check out https://wiki.apertium.org/wiki/Top_tips_for_GSOC_applications"
temporaryMessage = None

greetings = ('Hi', 'Hey', 'Hello', 'What\'s kicking', 'What\'s the good word', 'Top of the morning', 'Yo', 'What up', 'Sup', "What's hanging", "In the hood", "Kaixo", "Zer moduz", "Сәлем", "Қалың қалай", "Salom", "Привет", "No bugs is good bugs", "Mitä kuuluu", "حالت چطوره", "როგორა ხარ", "ինչպե՞ս ես", "сайн байна уу", "कैसे हो", "Como vai", "Nasılsın", "Ворчӏами", "Howdy", "你好", "여보세요", "こんにちは", "Bonjour", "Hola", "Goddag", "Goedendag", "नमस्ते", "Olá", "Здравствуйте", "नमस्कार", "Góðan dag", "Sveiki", "Hallo", "Salam", "Cześć", "Bună ziua", "Zdravo", "Ahoj", "Բարև", "Ողջույն", "Բարև Ձեզ", "Ինչպե՞ս եք", "Ինչպե՞ս են Ձեր գործերը", "Sveiki", "Zdravo", "Γειά σου", "გამარჯობა", "Вітання", "سلام", "Saluton", "Здравейте", "Сәлеметсіз бе", "Hola", "Як ти", "Здраво", "Πώς είσαι", "Как ты", "Здравствуй")

def countGuest(phenny, nick):
    global_filename = db_path(phenny, 'guests')
    if not os.path.exists(global_filename):
        try: f = open(global_filename, 'w')
        except OSError: pass
        f.write('')
        f.close()
    guests = {}
    with open(global_filename, 'r') as dbFile:
        guests = set(dbFile.read().strip().split(','))
    guests.add(nick)
    with open(global_filename, 'w') as dbFile:
        dbFile.write(','.join(guests))

def getGuests(phenny, input):
    if input.admin:
        global_filename = db_path(phenny, 'guests')
        if not os.path.exists(global_filename):
            try: f = open(global_filename, 'r')
            except OSError: pass
            f.close()
        guests = {}
        with open(global_filename, 'r') as dbFile:
            guests = set(dbFile.read().strip().split(','))
        phenny.say(str(guests))
    else:
        phenny.reply("That is an admin-only command.")


getGuests.name = 'getGuests'
getGuests.commands = ['getGuests']
getGuests.priority = 'low'
getGuests.thread = False


def hello(phenny, input):
    global temporaryMessage
    global emptyHellos
    global greetings

    nickname = phenny.nick
    greeting = random.choice(greetings)
    if not re.search(nickname, input) and temporaryMessage is not None:
        punctuation = random.choice(('.', '!', ';'))
        phenny.say(greeting + ' ' + input.nick + punctuation +temporaryMessage)
        countGuest(phenny, input.nick)
    elif emptyHellos:
        punctuation = random.choice(('', '!'))
        phenny.say(greeting + ' ' + input.nick + punctuation)
    elif re.search(nickname, input):
        punctuation = random.choice(('', '!'))
        phenny.say(greeting + ' ' + input.nick + punctuation)


#hello.rule = r'(?i)(hi|hello|hey|what\'s kickin[\'g]*|how you been|what\'s (.*)good(.*)|top o[\'f]* the mornin[\'g]*|what\'s hangin[\'g]*|yo|in the hood|in da hood|kaixo|zer moduz|с[әа]л[еао]м|wb) $nickname[ \t]*$'
#strings = "(?i)(hi|hello|hey|what\'s kickin[\'g]*|how you been|what\'s (.*)good(.*)|top o[\'f]* the mornin[\'g]*|what\'s hangin[\'g]*|yo|in the hood|in da hood|kaixo|zer moduz|с[әа]л[еао]м|s[ae]l[ao]m|wb)"
hello.rule = r'(?i)(?:$nickname[,:]* )?(hi|hello|hey|what\'s kickin[\'g]*|how you been|what\'s (.*)good(.*)|what\'s up|sup|(?:top o[\'f]* the )?mornin[\'g]*|what\'s hangin[\'g]*|yo|in the hood|in da hood|kaixo|zer moduz|с[әа]л[еао]м|s[ae]l[ao]m|wb|mitä kuuluu|როგორა ხარ|ինչպե՞ս ես|сайн байна уу|कैसे हो|como vai|привет|salut|n(?:в)орчӏами|nasılsın(?:ız)?)(?:[,]* $nickname)?[ \t!\.\?]*$'

def interjection(phenny, input):
    phenny.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

if __name__ == '__main__':
    print(__doc__.strip())
