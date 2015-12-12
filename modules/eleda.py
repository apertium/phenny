#!/usr/bin/env python

"""
eleda.py - Begiak Eleda Module
Any questions can go to Qasim Iqbal (nick: Qasim) (email: me@qas.im)
"""

import http.client
import re, json
import sys
#from apertium_translate import translate
import urllib.request, urllib.parse, urllib.error
import web
from tools import GrumbleError, translate

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
		self.dir = dir

def get_page(domain, url, encoding='utf-8'): #get the HTML of a webpage.
	conn = http.client.HTTPConnection(domain, 80, timeout=60)
	conn.request("GET", url, headers=headers)
	res = conn.getresponse()
	return res.read().decode(encoding)

def follow(phenny, input): #follow a user
	"""Follow someone and translate as they speak."""
	global follows
	
	if input.groups()[1] != None:
		data = input.group(2).split(' ')
		nick = data[0]
		
		if nick.lower() == phenny.config.nick.lower():
			phenny.reply(phenny.config.nick.upper() + " DOES NOT LIKE TO BE FOLLOWED.")
			return
			
		try:
			dir = data[1].split('-')
			dir[1] = dir[1]
		except:
			phenny.reply("Need language pair!")
			return
			
		pairs = get_page('api.apertium.org', '/json/listPairs')
		if '{"sourceLanguage":"'+dir[0]+'","targetLanguage":"'+dir[1]+'"}' not in pairs:
			phenny.reply("That language pair does not exist!")
			return
		
		if len(data) in [2,3]:
			sender = input.nick
			if len(data) == 3 and input.admin == True:
				#only accept follower paramter if it exists and the nick is admin
				sender = data[2]
		else:
			phenny.reply("Unexpected error.")
			return
			
		for i in follows:
			if i.nick == nick and i.dir == dir and i.sender == sender:
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
	for i in range(len(follows)):
		if follows[i].nick == input.groups()[1] and follows[i].sender == input.nick:
			#if this person is indeed being followed (and is indeed the creator of the follow)
			follows[i] = Eleda('', '', ['', ''])
			following = True
	if following == True:
		phenny.reply(input.groups()[1] + " is no longer being followed.")
	else:
		phenny.reply("Sorry, you aren't following that user!")

def following(phenny, input): #list followed users
	"""List people currently being followed."""
	text = []
	for i in follows:
		if i.nick != '':
			#populate list with following list
			text.append(i.nick + " (" + '-'.join(i.dir) + ") by " + i.sender)
	if len(text) < 1:
		phenny.reply("No one is being followed at the moment.")
	else:
		phenny.say('Users currently being followed: ' + ', '.join(text) + '. (Translations are private)')

def test(phenny, input): #filter through each message in the channel
	if input.sender == '#apertium' or input.sender == '#apertium_test':
		if input.groups()[0][0] == '.' or 'begiak: ' in input.groups()[0].split(' ')[0]:
			#do not translate if it is a begiak function
			return
		
		for i in follows:
			if i.nick != '':
				if i.nick == input.nick:
					#this user is being followed, translate them
					direction = '-'.join(i.dir)
					translation = translate(input.group(0), i.dir[0], i.dir[1])
					translation = translation.replace('*', '')
					if translation != input.group(0):
						#don't bother sending a notice if the input is the same as the output
						phenny.write(['NOTICE', i.sender], i.nick + ' (' + '-'.join(i.dir) + '): ' + translation)

follow.commands = ['follow']
follow.example = '.follow Qasim en-es'
unfollow.commands = ['unfollow']
unfollow.example = '.unfollow Qasim'
following.commands = ['following']
following.example = '.following'
test.rule = r'(.*)'