#!usr/bin/python3
"""
more.py - Message Buffer Interface
Author - mandarj
"""

import sqlite3
from tools import break_up, calling_module, DatabaseCursor, db_path, max_message_length
from bot import command, event

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

buffer_threshold = 2

def add_messages(phenny, target, messages, tag=None):
    if not type(messages) is list:
        messages = [messages]

    if not target.startswith('#'):
        messages = list(map(lambda message: target + ': ' + message, messages))

    messages = sum(map(lambda message: break_up(message), messages), [])

    if not tag:
        tag = calling_module()

    if len(messages) <= buffer_threshold:
        for message in messages:
            phenny.msg(target, message)

        return

    phenny.msg(target, messages.pop(0))
    phenny.msg(target, 'Type ".more" to view remaining {num} messages.'.format(num=len(messages)))

    target = target.casefold()

    with DatabaseCursor(phenny.more_db) as cursor:
        values = [(target, message, tag) for message in messages]
        cursor.executemany("INSERT INTO more (target, message, tag) VALUES (?, ?, ?)", values)

@event('JOIN')
def joinAlert(phenny, msg):
    if count_more(phenny, msg.nick):
        phenny.reply('You have queued messages. Type ".more", and I\'ll read them out.')

@command('more')
def more(phenny, msg):
    ''''.more [N] [tag]' shows queued messages.
    Optional N: number of messages to show
    Optional tag: which messages to show (usually a module name)'''

    count = 1
    tag = ''
    if msg.command_args_list:
        count = msg.command_args_list[0]
        if count.isdigit():
            count = int(count)
        else:
            return
        if len(msg.command_args_list) > 1:
            tag = msg.command_args_list[1]

    if count_more(phenny, msg.nick, tag):
        show_more(phenny, msg.nick, count, tag)
    elif count_more(phenny, msg.sender, tag):
        if phenny.is_admin(msg.nick):
            show_more(phenny, msg.sender, count, tag)
        else:
            phenny.reply("Only admins can use .more on channels.")
    else:
        phenny.reply("No more queued messages")

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

def delete_all(phenny, target=None):

    with DatabaseCursor(phenny.more_db) as cursor:
        if target:
            target = target.casefold()
            cursor.execute("DELETE FROM more WHERE target=?", (target,))
        else:
            cursor.execute("DELETE FROM more")
