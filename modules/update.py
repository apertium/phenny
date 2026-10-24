import subprocess
import os
import sys
from bot import command

@command('update', owner=True)
def update(phenny, msg):
    """.update - Make begiak check for updates and restart"""
    phenny.say("Pulling new source code...")
    if subprocess.call(['git', 'pull']) == 0:
        phenny.say("Successfully pulled...")
    else:
        phenny.say("Uh oh...")
        return 0

    phenny.say("Beginning to restart...")
    phenny.say("If I rejoin, I succeeded.")
    os.execv('./phenny', sys.argv)
