#!usr/bin/python3
"""
more.py - Message Buffer Interface
Author - mandarj
"""

import sqlite3
from tools import break_up, calling_module, DatabaseCursor, db_path, max_message_length

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

def add_messages(phenny, target, messages, tag=None):
    if not type(messages) is list:
        messages = [messages]

    if not target in phenny.config.channels:
        messages = list(map(lambda message: target + ': ' + message, messages))

    messages = sum(map(lambda message: break_up(message), messages), [])

    if not tag:
        tag = calling_module()

    if len(messages) <= 2:
        for message in messages:
            phenny.msg(target, message)
    else:
        phenny.msg(target, messages.pop(0))
        phenny.msg(target, 'Please type ".more" to view remaining messages.')

        target = target.casefold()

        with DatabaseCursor(phenny.more_db) as cursor:
            values = [(target, message, tag) for message in messages]
            cursor.executemany("INSERT INTO more (target, message, tag) VALUES (?, ?, ?)", values)

def joinAlert(phenny, input):
    if has_more(phenny, input.nick):
        phenny.say(input.nick + ': You have queued messages. Type ".more", and I\'ll read them out.')
joinAlert.event = 'JOIN'
joinAlert.rule = r'.*'

def more(phenny, input):
    ''''.more [N] [tag]' shows queued messages.
    Optional N: number of messages to show
    Optional tag: which messages to show (usually a module name)'''

    count = int(input.group(1)) if input.group(1) else 1
    tag = input.group(2)

    if has_more(phenny, input.nick, tag):
        show_more(phenny, input.sender, input.nick, count, tag)
    elif (input.admin or input.owner) and has_more(phenny, input.sender, tag):
        show_more(phenny, input.sender, input.sender, count, tag)
    else:
        phenny.reply("No more queued messages")

more.name = 'more'
more.rule = r'[.]more(?: ([1-9][0-9]*))?(?: (\S+))?'

def has_more(phenny, target, tag=None):
    target = target.casefold()

    with DatabaseCursor(phenny.more_db) as cursor:
        if tag:
            cursor.execute("SELECT COUNT(*) FROM more WHERE target=? AND tag=?", (target, tag))
        else:
            cursor.execute("SELECT COUNT(*) FROM more WHERE target=?", (target,))

        return cursor.fetchone()[0] > 0

def show_more(phenny, sender, target, count, tag=None):
    target = target.casefold()

    with DatabaseCursor(phenny.more_db) as cursor:
        if tag:
            cursor.execute("SELECT id, message FROM more WHERE target=? AND tag=? ORDER BY id ASC LIMIT ?", (target, tag, count))
        else:
            cursor.execute("SELECT id, message FROM more WHERE target=? ORDER BY id ASC LIMIT ?", (target, count))

        rows = cursor.fetchall()

        cursor.executemany("DELETE FROM more WHERE id=?", [(row[0],) for row in rows])

        if tag:
            cursor.execute("SELECT COUNT(*) FROM more WHERE target=? AND tag=?", (target, tag))
        else:
            cursor.execute("SELECT COUNT(*) FROM more WHERE target=?", (target,))

        remaining = cursor.fetchone()[0]

    messages = [row[1] for row in rows]

    if len(messages) > 1:
        for message in messages:
            phenny.msg(sender, message)

        if remaining > 0:
            phenny.msg(sender, str(remaining) + " message(s) remaining")
    else:
        message = messages[0]

        if remaining > 0:
            if len(message + " (" + str(remaining) + " remaining)") > max_message_length:
                phenny.msg(sender, message)
                phenny.msg(sender, str(remaining) + " message(s) remaining")
            else:
                phenny.msg(sender, message + " (" + str(remaining) + " remaining)")
        else:
            phenny.msg(sender, message)

def delete_all(phenny, target=None):

    with DatabaseCursor(phenny.more_db) as cursor:
        if target:
            target = target.casefold()
            cursor.execute("DELETE FROM more WHERE target=?", (target,))
        else:
            cursor.execute("DELETE FROM more")
