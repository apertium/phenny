#!/usr/bin/python3
"""
botfun.py - activities that bots do
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""
import random
from bot import keyword, command

@keyword(r'(?i).*((no|any|most|some|other|many|lot of|few|several|certain|никак.*|нет) (exception|исключени)).*$', priority='low')
def noexceptions(phenny, msg):
   """Tells someone there aren't ever any exceptions"""
   if not msg.nick:
      return phenny.say('NO EXCEPTIONS!')

   response = "NO EXCEPTIONS, %s!"
   phenny.say(response % msg.nick)

@command(['harglebargle', 'hargle'], priority='low', example='.harglebargle firespeaker')
def harglebargleP(phenny, msg):
   """Tells someone hargle bargle (cf. http://nedroidcomics.livejournal.com/224029.html , http://quotes.firespeaker.org/?id=1415)"""
   if msg.command_args.lower() == 'bargle':
       phenny.say('HARGLE BARGLE!')
       return
   whouser = msg.command_point or msg.command_args or msg.nick
   if not whouser:
      phenny.say('HARGLE BARGLE!')
      return
   response = "HARGLE BARGLE, %s!"
   phenny.say(response % whouser)

@keyword(r'(?i).*(hargle)((?![\s]*bargle).)*$', priority='low')
def bargle(phenny, msg):
   """Says bargle if someone says hargle (cf. http://nedroidcomics.livejournal.com/224029.html , http://quotes.firespeaker.org/?id=1415)"""
   if msg.text != "hargle bargle" and msg.text != "harglebargle":
      phenny.say("bargle!")

@keyword(r'(?i)((?!hargle[\s]*).)*(bargle).*$', priority='low')
def hargle(phenny, msg):
   """Says harglebargle if someone says bargle (cf. http://nedroidcomics.livejournal.com/224029.html , http://quotes.firespeaker.org/?id=1415)"""
   if msg.text != "hargle bargle" and msg.text != "harglebargle":
      phenny.say("HARGLE BARGLE!")

if __name__ == '__main__':
   print(__doc__.strip())

@keyword(r'(?i).*(udmurt).*$', priority='low')
def udmurt(phenny, msg):
   """expresses joy over mention of Udmurt"""
   phenny.say(r"\o/ \o/ \o/ U D M U R T \o/ \o/ \o/")

@keyword(r'(?i).*(particle|частиц|partikkel|pcle).*$', priority='low')
def particles(phenny, msg):
   """expresses sadness over mention of particles"""
   message = "this is my particles face :((((("
   whouser = msg.nick
   if not whouser:
      phenny.say(message)
   else:
      phenny.say("%s: %s" % (whouser, message))

@keyword(r'(?i).*(unsupervi(s|z)ed).*$', priority='low')
def unsupervised(phenny, msg):
   """various reactions to people talking about unsupervised stuff"""
   message = random.choice(['beam search should improve the results', 'use a perceptron', 'use EM to improve your results', 'unsupervised'])
   whouser = msg.nick
   if not whouser:
      phenny.say(message)
   else:
      phenny.say("%s: %s" % (whouser, message))

@keyword(r'(?i)(.* )?nn(\.|\!|)$', priority='low')
def nightnight(phenny, msg):
   """when people go to bed"""
   message = random.choice(['nn', 'night', 'жашкы жат', 'later', 'sweet dreams', 'o/'])
   whouser = msg.nick
   if not whouser:
      phenny.say(message)
   else:
      phenny.say("%s, %s!" % (message, whouser))

@keyword(r'(?i).*(u_dep|u_derp)$', priority='low')
def uderp(phenny, input):
   """when people talk about #u_dep"""
   message = random.choice([r'\o/ UD \o/', '（。々°） #u_dep', 'ᕕ(ᐛ)ᕗ #u_dep', 'universal derpendencies!', 'treegrams ftw!'])
   whouser = input.nick
   if not whouser:
      phenny.say(message)
   else:
      phenny.say("%s, %s!" % (message, whouser))
