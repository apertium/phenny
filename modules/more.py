#!usr/bin/python3
"""
more.py - Message Buffer Interface
Author - mandarj
"""

import sqlite3
from time import time
from tools import break_up, calling_module, DatabaseCursor, db_path, max_message_length

last_notified = {}
notify_interval = 60

def setup(self):
    self.more_db = db_path(self, 'more')

    connection = sqlite3.connect(self.more_db)
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS more (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        target     VARCHAR(255),
        message    VARCHAR({max_msg_len}),
        tag        VARCHAR(255)
    );'''.format(max_msg_len=max_message_length))

    cursor.close()
    connection.close()

def notify(phenny, target):
    target = target.casefold()
    count = count_more(phenny, target)
    now = time()

    if count and (last_notified.get(target, 0) - now > notify_interval):
        if target.startswith('#'):
            phenny.msg(target, "There are %s queued messages. Type '.more' to view." % (count))
        else:
            phenny.msg(target, "%s: You have %s queued messages. Type '.more' to view." % (target, count))

        last_notified[target] = now

def add_messages(phenny, target, messages, tag=None):
    if not type(messages) is list:
        messages = [messages]

    if not target.startswith('#'):
        messages = list(map(lambda message: target + ': ' + message, messages))

    messages = sum(map(lambda message: break_up(message), messages), [])

    if not tag:
        tag = calling_module()

    if not count_more(phenny, target, tag):
        phenny.msg(target, '[%s] %s' % (tag, messages.pop(0)))

    notify(phenny, target)

    target = target.casefold()

    with DatabaseCursor(phenny.more_db) as cursor:
        values = [(target, message, tag) for message in messages]
        cursor.executemany("INSERT INTO more (target, message, tag) VALUES (?, ?, ?)", values)

def joinAlert(phenny, input):
    notify(phenny, input.nick)
joinAlert.event = 'JOIN'
joinAlert.rule = r'.*'

def more(phenny, input):
    ''''.more [N] [tag]' shows queued messages.
    Optional N: number of messages to show
    Optional tag: which messages to show (usually a module name)'''

    count = int(input.group(1)) if input.group(1) else 1
    tag = input.group(2)

    if count_more(phenny, input.nick, tag):
        show_more(phenny, input.nick, count, tag)
    elif (input.admin or input.owner) and count_more(phenny, input.sender, tag):
        show_more(phenny, input.sender, count, tag)
    else:
        phenny.reply("No more queued messages")

more.name = 'more'
more.rule = r'[.]more(?: ([1-9][0-9]*))?(?: (\S+))?'

def count_more(phenny, target, tag=None):
    target = target.casefold()

    with DatabaseCursor(phenny.more_db) as cursor:
        if tag:
            cursor.execute("SELECT COUNT(*) FROM more WHERE target=? AND tag=?", (target, tag))
        else:
            cursor.execute("SELECT COUNT(*) FROM more WHERE target=?", (target,))

        return cursor.fetchone()[0]

def get_more(phenny, target, count, tag=None):
    target = target.casefold()

    with DatabaseCursor(phenny.more_db) as cursor:
        if tag:
            cursor.execute("SELECT id, message, tag FROM more WHERE target=? AND tag=? ORDER BY id ASC LIMIT ?", (target, tag, count))
        else:
            cursor.execute("SELECT id, message, tag FROM more WHERE target=? ORDER BY id ASC LIMIT ?", (target, count))

        rows = cursor.fetchall()

        cursor.executemany("DELETE FROM more WHERE id=?", [(row[0],) for row in rows])

    return [row[1:3] for row in rows]

def show_more(phenny, target, count, tag=None):
    rows = get_more(phenny, target, count, tag)
    remaining = count_more(phenny, target, tag)

    messages = [row[0] for row in rows]

    if len(messages) > 1:
        for message in messages:
            phenny.say(message)

        if remaining > 0:
            phenny.say(str(remaining) + " message(s) remaining")
    else:
        message = messages[0]

        if remaining > 0:
            if len(message + " (" + str(remaining) + " remaining)") > max_message_length:
                phenny.say(message)
                phenny.say(str(remaining) + " message(s) remaining")
            else:
                phenny.say(message + " (" + str(remaining) + " remaining)")
        else:
            phenny.say(message)

    last_notified[target] = time()

def delete_all(phenny, target=None):

    with DatabaseCursor(phenny.more_db) as cursor:
        if target:
            target = target.casefold()
            cursor.execute("DELETE FROM more WHERE target=?", (target,))
        else:
            cursor.execute("DELETE FROM more")
