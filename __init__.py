#!/usr/bin/env python3
"""
__init__.py - Phenny Init Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import glob
import logging
import os
from os.path import dirname, basename, isfile
import signal
import sys
import threading
import time

logger = logging.getLogger('phenny')


def all_modules(file):
    modules = glob.glob(dirname(file)+"/*.py")
    return [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

__all__ = all_modules(__file__)


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

    def connect():
        import bot
        p = bot.Phenny(config)
        p.use_sasl = config.sasl

        ssl_context = p.get_ssl_context(config.ca_certs)

        if config.ssl_cert and config.ssl_key:
            ssl_context.load_cert_chain(config.ssl_cert, config.ssl_key)

        p.run(config.host, config.port, config.ssl, config.ipv6, None,
              ssl_context)

    try:
        Watcher()
    except Exception as error:
        logger.warning(str(error) + ' (in __init__.py)')

    while True: 
        try:
            connect()
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
