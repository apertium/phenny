#!/usr/bin/env python
"""
away.py - Phenny's record or who's away/present module
"""

import os, re, time, random
import web

statuses = {"alan": "boom bitchezzzz"}

def whereis(phenny, input):
	"""Tells you nick's current status."""
	whereis_nick = input.split(" ")[1]
	print(input + " --> " + whereis_nick)
	if (whereis_nick.casefold() in list(statuses.keys())):
		phenny.reply(whereis_nick + " said: " + statuses[whereis_nick.casefold()])
	else:
		phenny.reply("Sorry, " + whereis_nick + " seems to be AWOL...")
whereis.commands = ["whereis"]
whereis.priority = 'low'
whereis.example = '.whereis sushain'
whereis.thread = False

def away(phenny, input):
	"""Set your status to being away."""
	nick = input.nick.casefold()
	if input.count(" ") == 0:
		statuses[nick] = "I'm away right now"
	else:
		message = str(" ".join(input.split(" ")[1:]))
		statuses[nick] = message
away.commands = ['away']
away.example = '.away eating pie'
away.priority = 'low'
away.thread = False

def back(phenny, input):
	"""Set your status to being available."""
	nick = input.nick.casefold()
	if input.count(" ") == 0:
		statuses[nick] = "I'm around at the minute"
	else:
		message = str(" ".join(input.split(" ")[1:]))
		statuses[nick] = message
back.commands = ['back']
back.example = '.back'
back.priority = 'low'
back.thread = False


if __name__ == '__main__': 
    print(__doc__.strip())
