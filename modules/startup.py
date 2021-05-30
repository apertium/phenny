#!/usr/bin/env python
"""
startup.py - Phenny Startup Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import logging
import threading
import time

logger = logging.getLogger('phenny')

def setup(phenny): 
    logger.info("Setting up phenny")
    # by clsn
    phenny.data = {}
    refresh_delay = 300.0

    if hasattr(phenny.config, 'refresh_delay'):
        try: refresh_delay = float(phenny.config.refresh_delay)
        except: pass

        def close():
            logger.info("Nobody PONGed our PING, restarting")
            phenny.handle_close()

        def pingloop():
            timer = threading.Timer(refresh_delay, close, ())
            phenny.data['startup.setup.timer'] = timer
            phenny.data['startup.setup.timer'].start()
            phenny.proto.ping(phenny.config.host)
        phenny.data['startup.setup.pingloop'] = pingloop

        def pong(phenny, input):
            try:
                phenny.data['startup.setup.timer'].cancel()
                time.sleep(refresh_delay + 60.0)
                pingloop()
            except: pass
        pong.event = 'PONG'
        pong.thread = True
        pong.rule = r'.*'

        phenny.variables.setdefault('startup', {})['pong'] = pong

def startup(phenny, input):
    import time

    # Start the ping loop. Has to be done after USER on e.g. quakenet
    if phenny.data.get('startup.setup.pingloop'):
        phenny.data['startup.setup.pingloop']()

    if hasattr(phenny.config, 'serverpass'): 
        phenny.proto.pass_(phenny.config.serverpass)
        logger.info(phenny.config.serverpass)

    if hasattr(phenny.config, 'password'): 
        logger.info("identifying with nickserv...")
        phenny.msg('NickServ', 'IDENTIFY %s' % phenny.config.password)
        logger.info("sent message to nickserv...")
    
    afterauth(phenny, input)

startup.rule = r'(.*)'
startup.event = '251'
startup.priority = 'low'

def afterauth(phenny, input):
    global afterauth

    logger.info('authed')
    # Cf. http://swhack.com/logs/2005-12-05#T19-32-36
    for channel in phenny.channels: 
        phenny.proto.join(channel)
        logger.info(channel)

    afterauth.event = None

afterauth.rule = r'.*identified for.*'
afterauth.event = 'NOTICE'
afterauth.priority = 'high'
afterauth.thread = False

if __name__ == '__main__': 
    print(__doc__.strip())
