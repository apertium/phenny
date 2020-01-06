#!/usr/bin/python3
import math
import os
import sqlite3
import time
import shlex
import datetime
import logging
import time
import modules.alias as aliasmodule
import modules.seen as seen
from threading import Lock, Thread
from tools import DatabaseCursor, db_path
from modules import caseless_list

lock = Lock()
users = set()

def make_table(cursor):
    cursor.execute('''create table if not exists users (
        nick        varchar(255) not null,
        github      varchar(255)         ,
        wiki        varchar(255)         ,
        timezone    varchar(255)         ,
        isgci       bool         not null,
        gciname     varchar(255)         ,
        isadmin     bool         not null,
        realname    varchar(255)         ,
        location    varchar(255)         ,
        unique (nick, github, wiki, gciname) on conflict replace
    );''')

def setup(self):
    self.whois_db = db_path(self, 'whois')

    connection = sqlite3.connect(self.greeting_db)
    cursor = connection.cursor()

    make_table(cursor)

    cursor.close()
    connection.close()

class Record:
    def __init__(self, datum):
        self.nick = datum[0]
        self.github = datum[1]
        self.wiki = datum[2]
        self.timezone = datum[3]
        self.isgci = datum[4]
        self.gciname = datum[5]
        self.isadmin = datum[6]
        self.realname = datum[7]
        self.location = datum[8]

def all_of(items):
    if len(items) == 0:
        return 'nothing'
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return '{} and {}'.format(items[0], items[1])
    else:
        response = ''
        for item in items[:len(items)-1]:
            response += '{}, '.format(item)
        response += 'and {}'.format(items[len(items)-1])
        return response

def whois(phenny, input):
    '''.whois <nick> - get info for registered nick; set data with .whoisset (see .help whoisset); admins or nick owners can drop with .whoisdrop <nick> '''
    bynick = True
    try:
        if len(input.group().split(' ', 1)) < 2:
            phenny.say('usage: .whois <query>')
            return 0

        text = input.group().split(' ', 1)[1]
        if text == phenny.nick:
            phenny.say('{} (Wondrous Guardian of {}) | IRC (all timezones) | now'.format(phenny.nick, all_of(phenny.channels)))
            return 0

        with DatabaseCursor(phenny.whois_db) as cursor:
            make_table(cursor)
            cursor.execute('select * from users')
            data = [Record(datum) for datum in cursor.fetchall()]

            user = None

            for record in data:
                if record.nick.lower() == text.lower():
                    user = record
                    break

            if user == None:
                aliasmodule.loadAliases(phenny)
                aliases = aliasmodule.aliasGroupFor(text)
                for alias in aliases:
                    for record in data:
                        if record.nick.lower() == alias.lower():
                            user = record
                            user.nick = text
                            break

            if user == None:
                #can't find by nick; try by other things
                text = input.group().split(' ', 1)[1]
                results = []
                for entry in data:
                    e = [ text.lower() in record.lower() for record in [entry.nick, entry.github, entry.wiki, entry.gciname, entry.realname] if record is not None]
                    if True in e:
                        results.append(entry)

                if results:
                    user = results[0]
                else:
                    try:
                        seen_string = ' They were last seen {}.'.format(seen.seen(text, phenny)['ago'])
                    except seen.NotSeenError:
                        seen_string = ''
                    phenny.say('Hmm... {} is not in the database. Apparently, they have not registered.{}'.format(text, seen_string))
                    return 0

        if user.timezone is None:
            if user.location is None:
                locstring = ''
            else:
                locstring = ' | {}'.format(user.location)
        else:
            if user.location is None:
                locstring = ' | {}'.format(user.timezone)
            else:
                locstring = ' | {} ({})'.format(user.location, user.timezone)

        try:
            seen_string = ' | {}'.format(seen.seen(user.nick, phenny)['ago'])
        except seen.NotSeenError:
            seen_string = ''
    
        realnamestring = ( ' ({})'.format(user.realname) if user.realname is not None else '')

        phenny.say('{}{}{}{}'.format(user.nick, realnamestring, locstring, seen_string))
    except Exception as e:
        phenny.say('Sorry, an error occurred.')
        raise e
whois.commands = ['whois']
whois.priority = 'medium'
whois.example = '.whois user'


def text_or_none(string):
    if string is 'x':
        return None
    else:
        return string


def whoisset(phenny, input):
    '''.whoisset <github> <wiki> <timezone> <realname> <location> - set whois info;
multiword values go in quotes;
all values are optional; use x to omit a value;
gci/gsoc mentors append name on gci tasks/gsoc to end of command;
gci/gsoc admins append 'admin' to end of command;
gci/gsoc admins/mentors, pls remember to rerun this command without gci/gsoc info after gci/gsoc ends'''
    try:
        text = shlex.split(input.group())
        if len(text) < 6:
            phenny.say('usage: .whoisset <github> <wiki> <timezone> <realname> <location>')
            return

        with DatabaseCursor(phenny.whois_db) as cursor:
            make_table(cursor)

            is_admin = False
            is_mentor = False

            try:
                gci_status = text[6]
                if gci_status == 'admin':
                    is_admin = True
                else:
                    is_mentor = True
            except Exception:
                pass

            cursor.execute('''delete from users where nick = ?;''', (input.nick,))
            cursor.execute('''insert into users values (?, ?, ?, ?, ?, ?, ?, ?, ?);''', (input.nick, text_or_none(text[1]), text_or_none(text[2]), text_or_none(text[3]), ( is_admin or is_mentor ) , (text[6] if is_mentor else None), is_admin, text_or_none(text[4]), text_or_none(text[5])))
            cursor.close()
        phenny.say('OK, I recorded all that. Type `.whois ' + input.nick + '` to verify it.')
    except Exception as e:
        phenny.say('Sorry, an error occurred.')
        phenny.say('Say `.help whoisset` in private chat with me to see usage.')
        raise e
whoisset.commands = ['whoisset']
whoisset.priority = 'medium'
whoisset.example = '.whoisset scoopgracie ScoopGracie utc-8:00 "Scoop Gracie" "Oregon, USA"'


def whoisdrop(phenny, input):
    '''.whoisdrop <nick> - drop a record from the whois database (must be <nick> or a phenny admin)'''
    try:
        try:
            text = input.group().split(' ')[1]
        except IndexError:
            phenny.say('usage: .whoisdrop <nick>')
            return

        if input.nick.casefold() in caseless_list(phenny.config.admins) or input.nick.lower() is text.lower():
            with DatabaseCursor(phenny.whois_db) as cursor:
                make_table(cursor)
                cursor.execute('''delete from users where nick = ?;''', (text,))
            phenny.say('{} has been removed from the database.'.format(text))
        else:
            phenny.say('You must be an admin to use this command.')
    except Exception as e:
        phenny.say('Sorry, an error occurred.')
        raise e
whoisdrop.commands = ['whoisdrop']
whoisdrop.priority = 'medium'


logger = logging.getLogger('phenny')

if __name__ == '__main__':
    print(__doc__.strip())
