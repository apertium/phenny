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


def whois(phenny, input):
    '''.whois <nick> - get whois for nick;
.whois only accepts irc nicks; to search by github username, wiki username, or gci/gsoc name, see .whoislookup'''
    bynick = True
    try:
        text = input.group().split(' ')[1]
        with DatabaseCursor(phenny.whois_db) as cursor:
            make_table(cursor)
            cursor.execute(
                'select * from users where nick = (?)',
                (text,)
            )
            try:
                data = cursor.fetchall()[0]
            except:
                aliasmodule.loadAliases(phenny)
                aliases = aliasmodule.aliasGroupFor(text)
                found = False
                for alias in aliases:
                    cursor.execute(
                        'select * from users where nick = (?)',
                        (alias,)
                    )
                    try:
                        data = cursor.fetchall()[0]
                        found = True
                        break
                    except:
                        pass

                if not found:
                    bynick = False
                    #can't find by nick; try by other things
                    text = input.group().split(' ', 1)[1]
                    with DatabaseCursor(phenny.whois_db) as cursor:
                        make_table(cursor)

                        cursor.execute(
                            'select * from users;',
                        )
                        data = cursor.fetchall()

                        cursor.close()

                    results = []
                    for entry in data:
                        e = [ text.lower() in record.lower() for record in [entry[0], entry[1], entry[2], entry[5], entry[7]] if record is not None]
                        if True in e:
                            results.append(entry)
                    if results:
                        data = results[0]
                    else:
                        phenny.say('Hmm... ' + text + ' is not in the database. Apparently, s/he has not registered.')
                        return 0
        if data[3] is None:
            if data[8] is None:
                locstring = ''
            else:
                locstring = ' | ' + data[8]
        else:
            if data[8] is None:
                locstring = ' | ' + data[3]
            else:
                locstring = ' | ' + data[8] + ' (' + data[3] + ')'

        nick = ( text if bynick else data[0] )
        phenny.say( nick + ( (' (' + data[7] + ')' ) if data[7] is not None else '') + locstring +  seen(nick, phenny))
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
        text = input.group().split(' ')[1]
        if input.nick.casefold() in caseless_list(phenny.config.admins) or input.nick.lower() is text.lower():
            with DatabaseCursor(phenny.whois_db) as cursor:
                make_table(cursor)
                cursor.execute('''delete from users where nick = ?;''', (text,))
            phenny.say(text + ' has been removed from the database.')
        else:
            phenny.say('You must be an admin to use this command.')
    except Exception as e:
        phenny.say('Sorry, an error occurred.')
        raise e
whoisdrop.commands = ['whoisdrop']
whoisdrop.priority = 'medium'


logger = logging.getLogger('phenny')

def seen(nick, phenny):
    if nick == "none":
        return ''

    logger_conn = sqlite3.connect(phenny.logger_db, detect_types=sqlite3.PARSE_DECLTYPES)

    cNick = ""
    cChannel = ""
    c = logger_conn.cursor()
    c.execute("select * from lines_by_nick where nick = ? order by datetime(last_time) desc limit 1", (nick,))
    cl = c.fetchone()
    try:
        cNick = cl[1]
        cChannel = cl[0]
        cLastTime = cl[4]
    except TypeError:
        return ''
    c.close()

    if cNick != "":
        dt = timesince(cLastTime)
        msg = " | last seen %s" % (dt)
        return msg

def timesince(td):
    seconds = int(abs(datetime.datetime.utcnow() - td).total_seconds())
    periods = [
        ('year', 60*60*24*365),
        ('month', 60*60*24*30),
        ('day', 60*60*24),
        ('hour', 60*60),
        ('minute', 60),
        ('second', 1)
    ]

    strings = []
    for period_name, period_seconds in periods:
            if seconds > period_seconds and len(strings) < 2:
                    period_value, seconds = divmod(seconds, period_seconds)
                    if period_value == 1:
                        strings.append("%s %s" % (period_value, period_name))
                    else:
                        strings.append("%s %ss" % (period_value, period_name))

    return "just now" if len(strings) < 1 else " and ".join(strings) + " ago"

if __name__ == '__main__':
    print(__doc__.strip())
