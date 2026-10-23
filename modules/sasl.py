#!/usr/bin/env python3
"""
sasl.py - phenny SASL Authentication module
"""
import base64
import logging
from bot import event

logger = logging.getLogger('phenny')

@event('CAP')
def irc_cap(phenny, msg):
	value, cap = msg.args[0], msg.args[3]
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

@event('AUTHENTICATE')
def irc_authenticated(phenny, msg):
	auth = None

	nick = phenny.config.nick
	password = phenny.config.password

	auth = "\0".join((nick, nick, password))
	auth = base64.b64encode(str.encode(auth))

	if auth is None:
		irc_cap_end()

	while len(auth) >= 400:
		out = auth[0:400]
		auth = auth[401:]
		phenny.write(('AUTHENTICATE', out))
	phenny.write(('AUTHENTICATE', auth))

@event('903')
def irc_903(phenny, msg):
	irc_cap_end(phenny, input)
	logger.info('SASL Authentication successful. ')

@event('904')
def irc_904(phenny, input):
	irc_cap_end(phenny, input)
	logger.error('SASL Authentication failed: Wrong credentials.')

@event('905')
def irc_905(phenny, input):
	irc_cap_end(phenny, input)
	logger.error('SASL Authentication failed: Message too long (up to 400 bytes). ')

@event('906')
def irc_906(phenny, input):
	irc_cap_end(phenny, input)
	logger.error('SASL Authentication failed: Cannot use \'*\' with AUTHENTICATE.')

@event('907')
def irc_907(phenny, input):
	irc_cap_end(phenny, input)
	logger.error('SASL Authentication failed: You have already authenticated using SASL. ')

@event('908')
def irc_908(phenny, input):
	logger.error('SASL Authentication failed: Unsupported mechanism.')

def irc_cap_end(phenny, input):
	phenny.write(('CAP', 'END'))

if __name__ == '__main__':
	print(__doc__.strip())
