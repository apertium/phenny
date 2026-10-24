#!/usr/bin/python3
"""
commit.py - what the commit
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import web
from bot import command

@command('commit')
def commit(phenny, input):
    """.commit - Get a What the Commit commit message."""

    msg = web.get("http://whatthecommit.com/index.txt")
    phenny.reply(msg)

if __name__ == '__main__':
    print(__doc__.strip())
