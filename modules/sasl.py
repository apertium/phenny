#!/usr/bin/env python
"""
sasl.py - phenny SASL Authentication module
"""
import base64

def irc_cap (phenny, input):

	value, cap = input.args[0], input.args[3]
	rq = ''

	if cap == 'LS':
		if 'multi-prefix' in value:
			rq += ' multi-prefix'
		if 'sasl' in value:
			rq += ' sasl'

		if not rq:
			irc_cap_end(phenny, input)
		else:
			if rq[0] == ' ':
				rq = rq[1:]

			phenny.write(('CAP', 'REQ', ':' + rq))

	elif cap == 'ACK':
		if 'sasl' in value:
			phenny.write(('AUTHENTICATE', 'PLAIN'))
		else:
			irc_cap_end(phenny, input)
	else:
		irc_cap_end(phenny, input)

	return
irc_cap.rule = r'(.*)'
irc_cap.event = 'CAP'
irc_cap.priority = 'high'


def irc_authenticated (phenny, input):
	auth = None
	
	nick = phenny.config.nick
	password = phenny.config.password

	if hasattr(phenny.config, 'user') and phenny.config.user is not None:
		user = phenny.config.user
	else:
		user = nick

	auth = "\0".join((nick, user, password))
	auth = base64.b64encode(str.encode(auth))

	if auth is None:
		irc_cap_end()
		return

	while len(auth) >= 400:
		out = auth[0:400]
		auth = auth[401:]
		phenny.write(('AUTHENTICATE', out))
	phenny.write(('AUTHENTICATE', auth))

	return
irc_authenticated.rule = r'(.*)'
irc_authenticated.event = 'AUTHENTICATE'
irc_authenticated.priority = 'high'


def irc_903 (phenny, input):
	phenny.is_authenticated = True
	irc_cap_end(phenny, input)
	return
irc_903.rule = r'(.*)'
irc_903.event = '903'
irc_903.priority = 'high'


def irc_904 (phenny, input):
	irc_cap_end(phenny, input)
	return
irc_904.rule = r'(.*)'
irc_904.event = '904'
irc_904.priority = 'high'


def irc_905 (phenny, input):
	irc_cap_end(phenny, input)
	return
irc_905.rule = r'(.*)'
irc_905.event = '905'
irc_905.priority = 'high'


def irc_906 (phenny, input):
	irc_cap_end(phenny, input)
	return
irc_906.rule = r'(.*)'
irc_906.event = '906'
irc_906.priority = 'high'


def irc_907 (phenny, input):
	irc_cap_end(phenny, input)
	return
irc_907.rule = r'(.*)'
irc_907.event = '907'
irc_907.priority = 'high'


def irc_001 (phenny, input):
	phenny.is_connected = True
	return
irc_001.rule = r'(.*)'
irc_001.event = '001'
irc_001.priority = 'high'


def irc_cap_end (phenny, input):
	phenny.write(('CAP', 'END'))
	return


if __name__ == '__main__':
	print(__doc__.strip())