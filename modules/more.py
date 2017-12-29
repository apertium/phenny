#!usr/bin/python3
"""
more.py - Message Buffer Interface
Author - mandarj
"""

import sqlite3
from tools import break_up, DatabaseCursor, db_path, MAX_MSG_LEN

def setup(self):
    self.more_db = db_path(self, 'more')

    connection = sqlite3.connect(self.more_db)
    cursor = connection.cursor()

    cursor.execute('''create table if not exists more (
        target        varchar(255),
        message       varchar(''' + MAX_MSG_LEN + ''')
        identifier    integer primary key autoincrement
    );''')

    cursor.close()
    connection.close()

def add_messages(target, phenny, msgs):
    if not type(msgs) is list:
        msgs = [msgs]

    if not target in phenny.config.channels:
        msgs = list(map(lambda msg: target + ': ' + msg, msgs))

    msgs = sum(map(lambda msg: break_up(msg), msgs), [])

    if len(msgs) <= 2:
        for msg in msgs:
            phenny.msg(target, msg)
    else:
        phenny.msg(target, msgs.pop(0))
        phenny.msg(target, 'you have ' + str(len(msgs)) + ' more message(s). Please type ".more" to view them.')

        target = target.casefold()

        with DatabaseCursor(self.more_db) as cursor:
            values = [(target, message) for message in messages]
            cursor.executemany("INSERT INTO more (target, message) VALUES (?, ?)", values)

def more(phenny, input):
    ''' '.more N' prints the next N messages.
        If N is not specified, prints the next message.'''

    count = 1 if input.group(1) is None else int(input.group(1))

    if has_more(phenny, input.nick):
        show_more(phenny, input.sender, input.nick, count)
    elif (input.admin or input.owner) and has_more(phenny, input.sender):
        show_more(phenny, input.sender, input.sender, count)
    else:
        phenny.reply("No more queued messages")

more.name = 'more'
more.rule = r'[.]more(?: ([1-9][0-9]*))?'

def has_more(phenny, target):
    target = target.casefold()

    with DatabaseCursor(self.more_db) as cursor:
        cursor.execute("SELECT COUNT(*) FROM more WHERE target=?", (target,))
        return cursor.fetchone()[0] > 0

def show_more(phenny, sender, target, count):
    target = target.casefold()

    with DatabaseCursor(self.more_db) as cursor:
        cursor.execute("SELECT message, identifier FROM more WHERE target=? SORT BY identifier ASC LIMIT ?", (target, count))
        rows = cursor.fetchall()

        cursor.executemany("DELETE FROM more WHERE identifier=?", [(row[1],) for row in rows])

        cursor.execute("SELECT COUNT(*) FROM more WHERE target=?", (target,))
        remaining = cursor.fetchone()[0]

    messages = [row[0] for row in rows]

    if len(messages) > 1:
        for message in messages:
            phenny.msg(sender, message)

        if remaining > 0:
            phenny.msg(sender, str(remaining) + " message(s) remaining")
    else:
        message = messages[0]

        if remaining > 0:
            phenny.msg(sender, message + " (" + str(remaining) + " remaining)")
        else:
            phenny.msg(sender, message)
