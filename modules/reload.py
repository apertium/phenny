#!/usr/bin/env python
"""
reload.py - Phenny Module Reloader Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import importlib.util
import importlib.machinery
import os
import sys
import time
from bot import module_control

def restart(phenny):
    for module in phenny.modules:
        module_control(phenny, module, 'teardown')

    os.execv('phenny', sys.argv)

def f_reload(phenny, input):
    """Reloads a module, for use by admins only."""
    if not (input.admin or input.owner): return

    name = input.group(1)

    if (not name) or (name == '*'):
        restart(phenny)
        return

    if name not in phenny.modules:
        return phenny.reply("No '%s' module loaded" % name)
    module = phenny.modules[name]

    # Thanks to moot for prodding me on this
    path = module.__file__
    if path.endswith('.pyc') or path.endswith('.pyo'):
        path = path[:-1]
    if not os.path.isfile(path):
        return phenny.reply('Found %s, but not the source file' % name)

    module_control(phenny, module, 'teardown')
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_file_location(name, path, loader=loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    phenny.modules[name] = module
    module_control(phenny, module, 'setup')

    mtime = os.path.getmtime(module.__file__)
    modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))

    phenny.register(module)
    phenny.bind_commands()

    phenny.reply('%r (version: %s)' % (module, modified))
f_reload.name = 'reload'
f_reload.rule = ('$nick', ['reload'], r'(\S+)?')
f_reload.priority = 'low'
f_reload.thread = False

if __name__ == '__main__':
    print(__doc__.strip())
