#!/usr/bin/env python3
"""
alias.py - Phenny Alias Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

from tools import GrumbleError, read_db, write_db

# nick aliases (saved in ~/<User phenny dir>/<nick>-<host>.alias.db)
# format (each row is an alias group, aliases are separated by '\t'): 
#
# spectre\tspectie\tspectei
# nick\talias
nick_aliases = [] #don't change this, use the '.alias add' command on the bot

# pending alias pair requests
# reset each session
nick_pairs = []

def aliasGroupFor(nick1):
    # Returns a list containing all aliases for nick1 (including nick1)
    # If there are no recorded aliases, it returns a list only containing nick1
    for alias_group in nick_aliases:
        if nick1 in alias_group:
            return alias_group
    return [nick1]

def aliasPairMerge(phenny, nick1, nick2):
    #Merges the alias group that nick1 is in with the one nick2 is in
    #The resulting group is stored in nick_aliases
    group1 = aliasGroupFor(nick1)
    if len(group1) > 1: #group is in nick_aliases
        nick_aliases.remove(group1)

    group2 = aliasGroupFor(nick2)
    if len(group2) > 1: #group is in nick_aliases
        nick_aliases.remove(group2)

    group1.extend(group2)

    nick_aliases.append(group1)

    dumpAliases(phenny)

def alias(phenny, raw):
    if raw.group(1) :
        if raw.group(1) == 'add':
            nick1 = raw.nick
            nick2 = raw.group(2)
            if (nick2 == None):
                phenny.reply("Usage: .alias add <nick>")
            elif (nick1 == nick2):
                phenny.reply("I don't think that will be necessary.")
            elif (nick2 in aliasGroupFor(nick1)):  
                phenny.reply("You and " + nick2 + " are already paired.")
            elif ([nick2, nick1] in nick_pairs):
                nick_pairs.remove([nick2, nick1])
                aliasPairMerge(phenny, nick1, nick2)
                phenny.reply("Confirmed alias request with " + nick2 + ". Your current aliases are: " + ', '.join(aliasGroupFor(nick1)) + ".")
            elif ([nick1, nick2] in nick_pairs):
                phenny.reply("Alias request already exists. Switch your nick to " + nick2 + " and call \".alias add " + nick1 + "\" to confirm.")
            else:
                nick_pairs.append([nick1, nick2])
                phenny.reply("Alias request created. Switch your nick to " + nick2 + " and call \".alias add " + nick1 + "\" to confirm.")
        elif raw.group(1) == 'list':
            if raw.group(2):
                nick = raw.group(2)
                phenny.reply("%s's current aliases are: " % nick + ', '.join(aliasGroupFor(nick)) + ".")
            else:
               phenny.reply("Your current aliases are: " + ', '.join(aliasGroupFor(raw.nick)) + ".")
        elif raw.group(1) == 'remove':
            nick = raw.nick
            group = aliasGroupFor(nick)
            if len(group) > 1:
                nick_aliases.remove(group)
                group.remove(nick)
                nick_aliases.append(group)
                dumpAliases(phenny)
            phenny.reply("You have removed %s from its alias group" % nick)
        else:
            phenny.reply("Usage: .alias add <nick>, .alias list <nick>?, .alias remove")
    else:
        phenny.reply("Usage: .alias add <nick>, .alias list <nick>?, .alias remove")

alias.rule = r'\.alias(?:\s(\S+))?(?:\s(\S+))?'

def loadAliases(self):
    try:
        nick_aliases = read_db(self, 'alias')
    except GrumbleError:
        nick_aliases = []

def dumpAliases(self):
    write_db(self, 'alias', nick_aliases)

