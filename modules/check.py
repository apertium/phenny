from bot import command
@command('checkup')
def checkup(phenny, input):
    """.checkup - Check if begiak is up"""
    phenny.say("Status: online")
