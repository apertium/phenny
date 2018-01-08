#!/usr/bin/env python3
"""
__init__.py - Phenny Init Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import logging
import os
import signal
import sys
import threading
import time

logger = logging.getLogger('phenny')

class Watcher(object): 
    # Cf. http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496735
    def __init__(self):
        self.child = os.fork()
        if self.child != 0:
            signal.signal(signal.SIGTERM, self.sig_term)
            self.watch()

    def watch(self):
        try: os.wait()
        except KeyboardInterrupt:
            self.kill()
        sys.exit()

    def kill(self):
        try: os.kill(self.child, signal.SIGKILL)
        except OSError: pass

    def sig_term(self, signum, frame):
        self.kill()
        sys.exit()

def run_phenny(config): 
    if hasattr(config, 'delay'): 
        delay = config.delay
    else:
        delay = 20

    try:
        Watcher()
    except Exception as error:
        logger.warning(str(error) + ' (in __init__.py)')

    try:
        import bot
        p = bot.Phenny(config)
    except KeyboardInterrupt:
        sys.exit()

    while True: 
        try:
            p.run(config.host, config.port, config.ssl, config.ipv6, config.ca_certs)
        except KeyboardInterrupt:
            sys.exit()

        if not isinstance(delay, int):
            break

        logger.warning('Disconnected. Reconnecting in %s seconds...' % delay)
        time.sleep(delay)

def run(config): 
    t = threading.Thread(target=run_phenny, args=(config,))
    if hasattr(t, 'run'):
        t.run()
    else: t.start()

if __name__ == '__main__':
    print(__doc__)
