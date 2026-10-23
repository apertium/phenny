#!/usr/bin/python3
import math
import os
import sqlite3
import time
from threading import Lock, Thread
from tools import DatabaseCursor, db_path
from bot import command, event

lock = Lock()
users = set()

def setup(self):
    self.greeting_count = {}

    self.greeting_db = db_path(self, 'greeting')

    connection = sqlite3.connect(self.greeting_db)
    cursor = connection.cursor()

    cursor.execute('''create table if not exists special_nicks (
        message     varchar(255),
        nick        varchar(255),
        channel     varchar(255),
        unique (channel, nick) on conflict replace
    );''')

    cursor.execute('''create table if not exists opted_out (
        nick varchar(255)
    );''')

    cursor.close()
    connection.close()

@event('JOIN')
def greeting(phenny, msg):
    with lock: users.add(msg.nick)
    with DatabaseCursor(phenny.greeting_db) as cursor:
        cursor.execute('select nick from opted_out')
        rows = cursor.fetchall()
        opted_out_of_m = []
        for row in rows:
            opted_out_of_m.append(row[0])

    if "[m]" in msg.nick and not msg.nick in opted_out_of_m:
        hint = "Please consider removing [m] from your IRC nick. See https://wiki.apertium.org/wiki/IRC/Matrix#Remove_.5Bm.5D_from_your_IRC_nick for details. Reply .dismiss to prevent this message from appearing again."
        phenny.msg(msg.nick, msg.nick + ": " + hint)

    if msg.sender.casefold() not in phenny.config.greetings.keys():
        return

    time.sleep(phenny.config.greet_delay)

    if msg.nick not in users:
        return

    greetingmessage = phenny.config.greetings[msg.sender.casefold()]
    greetingmessage = greetingmessage.replace("%name", msg.nick)
    greetingmessage = greetingmessage.replace("%channel", msg.sender)

    nick = msg.nick.casefold()

    with DatabaseCursor(phenny.greeting_db) as cursor:
        cursor.execute("SELECT * FROM special_nicks WHERE nick = ?", (nick,))

        try:
            phenny.msg(msg.nick, msg.nick + ": " + str(cursor.fetchone()[0]))
            return
        except TypeError:
            pass

    with DatabaseCursor(phenny.logger_db) as cursor:
        cursor.execute("SELECT * FROM lines_by_nick WHERE nick = ?", (nick,))

        if cursor.fetchone() is None:
            if nick != phenny.config.nick.casefold():
                if nick not in phenny.greeting_count:
                    phenny.greeting_count[nick] = 0

                    help_text = "You will need to register your nick with NickServ. Type /msg NickServ HELP for information on getting started with this."
                    phenny.msg(msg.nick, help_text)
                    phenny.notice(msg.nick, help_text)

                phenny.greeting_count[nick] += 1

                if math.log2(phenny.greeting_count[nick]) % 1 == 0:
                    phenny.msg(msg.nick, greetingmessage)

@event('QUIT')
def quitting(phenny, msg):
    with lock: users.discard(msg.nick)

@event('PART')
def parting(phenny, msg):
    with lock: users.discard(msg.nick)

@event('KICK')
def kicked(phenny, msg):
    with lock: users.discard(msg.args[2])

@event('NICK')
def nickchange(phenny, msg):
    with lock:
        users.discard(msg.nick)
        users.add(msg.args[1])

@command('greeting', admin=True)
def greeting(phenny, msg):
    if ' ' not in msg.command_args:
        return
    mode, name = msg.command_args.split(' ', 1)
    if mode.lower() == 'add':
        if ' ' not in name:
            return
        name, message = name.split(' ', 1)
        sqlite_data = {
            'channel': msg.sender,
            'nick': name.lower(),
            'message': message,
        }
        with DatabaseCursor(phenny.greeting_db) as cursor:
            cursor.execute(
                '''insert or replace into special_nicks
                (channel, nick, message)
                values(:channel, :nick, :message);''', sqlite_data)
            cursor.execute('update special_nicks set message=:message where channel=:channel and nick=:nick', sqlite_data)

        phenny.reply("Successfully added " + name + " to the special greetings list.")
    elif mode.lower == 'del':
        with DatabaseCursor(phenny.greeting_db) as cursor:
            cursor.execute("DELETE FROM special_nicks WHERE nick = ? AND channel = ?", (name.lower(), msg.sender))

            phenny.reply("Successfully deleted " + name + " from the special greetings list.")

@command('dismiss')
def dismiss(phenny, msg):
    try:
        with DatabaseCursor(phenny.greeting_db) as cursor:
            cursor.execute(
                'insert into opted_out (nick) values (?)',
                (msg.nick,)
            )
        phenny.say('I won\'t tell you again.')
    except Exception as e:
        phenny.say('Sorry, an error occurred.')
        raise e

if __name__ == '__main__':
    print(__doc__.strip())
