#!/usr/bin/python3
import math
import os
import sqlite3
import time
from threading import Lock, Thread
from tools import DatabaseCursor, db_path

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

    cursor.close()
    connection.close()

def greeting(phenny, input):
    with lock: users.add(input.nick)
    try:
        opted_out_list = open(os.getenv('HOME') + '/.phenny/opted_out_of_matrix_message.json')
        opted_out_of_m = json.load(opted_out_list)
        opted_out_list.close()
    except:
        opted_out_of_m = []

    if "[m]" in input.nick and not input.nick in opted_out_of_m:
        hint = "Please consider removing [m] from your IRC nick. See http://wiki.apertium.org/wiki/IRC/Matrix#Remove_.5Bm.5D_from_your_IRC_nick for details. Reply .dismiss to prevent this message from appearing again."
        phenny.msg(input.nick, input.nick + ": " + hint)

    if input.sender.casefold() not in phenny.config.greetings.keys():
        return

    time.sleep(phenny.config.greet_delay)

    if input.nick not in users:
        return

    greetingmessage = phenny.config.greetings[input.sender.casefold()]
    greetingmessage = greetingmessage.replace("%name", input.nick)
    greetingmessage = greetingmessage.replace("%channel", input.sender)

    nick = input.nick.casefold()

    with DatabaseCursor(phenny.greeting_db) as cursor:
        cursor.execute("SELECT * FROM special_nicks WHERE nick = ?", (nick,))

        try:
            phenny.msg(input.nick, input.nick + ": " + str(cursor.fetchone()[0]))
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
                    phenny.msg(input.nick, help_text)
                    phenny.proto.notice(input.nick, help_text)

                phenny.greeting_count[nick] += 1

                if math.log2(phenny.greeting_count[nick]) % 1 == 0:
                    phenny.msg(input.nick, greetingmessage)

greeting.event = "JOIN"
greeting.priority = 'low'
greeting.rule = r'(.*)'

def quitting(phenny, input):
    with lock: users.discard(input.nick)

quitting.event = "QUIT"
quitting.rule = r'(.*)'

def parting(phenny, input):
    with lock: users.discard(input.nick)

parting.event = "PART"
parting.rule = r'(.*)'

def kicked(phenny, input):
    with lock: users.discard(input.args[2])

kicked.event = "KICK"
kicked.rule = r'(.*)'

def nickchange(phenny, input):
    with lock:
        users.discard(input.nick)
        users.add(input.args[1])

nickchange.event = "NICK"
nickchange.rule = r'(.*)'

def greeting_add(phenny, input):
    if not input.admin:
        phenny.reply("You have insufficient privelleges to use this command.")
        return

    if input.group(2) is None:
        phenny.reply("You haven't specified a name and message.")
        return
    elif len(input.group(2).split(" ")) < 2:
        phenny.reply("You haven't specified a message.")
        return

    sqlite_data = {
        'channel': input.sender,
        'nick': input.group(2).split(" ")[0].casefold(),
        'message': input.group(2).split(" ", 1)[1]
    }

    with DatabaseCursor(phenny.greeting_db) as cursor:
        cursor.execute('''insert or replace into special_nicks
                          (channel, nick, message)
                          values(:channel, :nick, :message);''', sqlite_data)
        cursor.execute('update special_nicks set message=:message where channel=:channel and nick=:nick', sqlite_data)

    phenny.reply("Successfully added " + input.group(2).split(" ", 1)[0] + " to the special greetings list.")

greeting_add.rule = (['greeting add'], r'(.*)')
greeting_add.name = 'greeting add'
greeting_add.priority = 'low'

def greeting_del(phenny, input):
    if not input.admin:
        phenny.reply("You have insufficient privelleges to use this command.")
        return

    if input.group(2) == None:
        phenny.reply ("You haven't specified a name.")
        return

    with DatabaseCursor(phenny.greeting_db) as cursor:
        cursor.execute("DELETE FROM special_nicks WHERE nick = ? AND channel = ?", (input.group(2).split(" ")[0].casefold(), input.sender))

    phenny.reply("Successfully deleted " + input.group(2).split(" ", 1)[0] + " from the special greetings list.")
greeting_del.rule = (['greeting del'], r'(.*)')
greeting_del.name = 'greeting del'
greeting_del.priority = 'low'


if __name__ == '__main__':
    print(__doc__.strip())
