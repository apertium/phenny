#!/usr/bin/env python

"""
eleda.py - Begiak Eleda Module
Any questions can go to Qasim Iqbal (nick: Qasim) (email: me@qas.im)
"""

import http.client
import re
import json
import sys
import urllib.request, urllib.parse, urllib.error
import web
from tools import GrumbleError, translate
from modules import caseless_equal
from web import get_page

follows = []

headers = {
   'User-Agent': 'Mozilla/5.0' + '(X11; U; Linux i686)' + 'Gecko/20071127 Firefox/2.0.0.11'
}

class Eleda(object):
	sender = ""
	nick = ""
	dir = []
	def __init__(self, sender, nick, dir):
		self.sender = sender
		self.nick = nick
		self.dir = tuple(dir)

def follow(phenny, input): #follow a user
	"""Follow someone and translate as they speak."""
        # TODO: what if the nick is not present in the channel?
        # phenny possibly informs sender that the nick is not present and continues?

	global follows

	if input.groups()[1] != None:
		data = input.group(2).split(' ')
		nick = data[0]

		if caseless_equal(nick, phenny.config.nick):
			phenny.reply(phenny.config.nick.upper() + " DOES NOT LIKE TO BE FOLLOWED.")
			return

		try:
			dir = data[1].split('-')
			dir[1] = dir[1]
		except:
			phenny.reply("Need language pair!")
			return

		pairs = {}
		if hasattr(phenny.config, 'translate_url'):
			pairs = json.loads(get_page(self.phenny.config.translate_url, '/listPairs'))
		else:
			pairs = json.loads(get_page('apy.projectjj.com', '/listPairs', port=2737))
		if {"targetLanguage":dir[1], "sourceLanguage":dir[0]} not in pairs["responseData"]:
			if (not(phenny.iso_conversion_data.get(dir[0])) or not(phenny.iso_conversion_data.get(dir[1])) or
				{"targetLanguage":phenny.iso_conversion_data.get(dir[1]),"sourceLanguage":phenny.iso_conversion_data.get(dir[0])} not in pairs["responseData"]):
				phenny.reply("That language pair does not exist!")
				return
			else:
				dir[0] = phenny.iso_conversion_data[dir[0]]
				dir[1] = phenny.iso_conversion_data[dir[1]]

		if len(data) in [2,3]:
			sender = input.nick
			if len(data) == 3 and input.admin == True:
				#only accept follower paramter if it exists and the nick is admin
				sender = data[2]
		else:
			phenny.reply("Unexpected error.")
			return

		for i in follows:
			if caseless_equal(i.nick, nick) and i.dir == tuple(dir) and caseless_equal(i.sender, sender):
				phenny.say(sender + " is already following " + nick + " with " + '-'.join(dir) + '.')
				return

		follows.append(Eleda(sender, nick, dir))
		phenny.reply(sender + " now following " + nick + " (" + '-'.join(dir) + ").")
	else:
		phenny.reply("Need nick and language pair!")

def unfollow(phenny, input): #unfollow a user
	"""Stop following someone."""
	global follows

	following = False
	for i in follows:
		if caseless_equal(i.nick, input.groups()[1]) and caseless_equal(i.sender, input.nick):
			#if this person is indeed being followed (and is indeed the creator of the follow)
			follows.remove(i)
			following = True
	if following == True:
		phenny.reply(input.groups()[1] + " is no longer being followed.")
	else:
		phenny.reply("Sorry, you aren't following that user!")

def following(phenny, input): #list followed users
	"""List people currently being followed."""
	text = []
	for i in follows:
		#populate list with following list
		text.append(i.nick + " (" + '-'.join(i.dir) + ") by " + i.sender)
	if len(text) < 1:
		phenny.reply("No one is being followed at the moment.")
	else:
		phenny.say('Users currently being followed: ' + ', '.join(text) + '. (Translations are private)')

def checkMessages(phenny, input): #filter through each message in the channel
	if input.sender in phenny.channels:
		if input.groups()[0][0] == '.' or (phenny.nick + ': ' or phenny.nick + ', ') in input.groups()[0].split(' ')[0]:
			#do not translate if it is a begiak function
			return

		translations = {}
		for i in follows:
			if caseless_equal(i.nick, input.nick):
				if (i.nick, i.dir) not in translations:
					#this user is being followed, translate them
					direction = '-'.join(i.dir)
					translations[(i.nick, i.dir)] = translate(phenny, input.group(0), i.dir[0], i.dir[1])
					translations[(i.nick, i.dir)] = translations[(i.nick, i.dir)].replace('*', '')
				if translations[(i.nick, i.dir)] != input.group(0):
					#don't bother sending a notice if the input is the same as the output
					phenny.msg(i.sender, i.nick + ' (' + '-'.join(i.dir) + '): ' + translations[(i.nick, i.dir)])

follow.commands = ['follow']
follow.example = '.follow Qasim en-es'
unfollow.commands = ['unfollow']
unfollow.example = '.unfollow Qasim'
following.commands = ['following']
following.example = '.following'
checkMessages.rule = r'(.*)'
