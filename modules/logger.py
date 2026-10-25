#!/usr/bin/python3
"""
logger.py - logger for privacy-protecting IRC stats
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import os
import random
import sqlite3
from tools import DatabaseCursor, db_path
from bot import every_message

def setup(self):
    self.logger_db = db_path(self, 'logger')

    connection = sqlite3.connect(self.logger_db)
    cursor = connection.cursor()

    cursor.execute('''create table if not exists lines_by_nick (
        channel     varchar(255),
        nick        varchar(255),
        lines       unsigned big int not null default 0,
        characters  unsigned big int not null default 0,
        last_time   timestamp default CURRENT_TIMESTAMP,
        quote       text,
        unique (channel, nick) on conflict replace
    );''')

    cursor.close()
    connection.close()

@every_message
def logger(phenny, msg):
    sqlite_data = {
        'channel': msg.sender,
        'nick': msg.nick.casefold(),
        'msg': msg.text,
        'chars': len(msg.text),
    }

    # format action messages
    if sqlite_data['msg'][:8] == '\x01ACTION ':
        sqlite_data['msg'] = '* {0} {1}'.format(sqlite_data['nick'], sqlite_data['msg'][8:-1])

    with DatabaseCursor(phenny.logger_db) as cursor:
        cursor.execute('''insert or replace into lines_by_nick
                    (channel, nick, lines, characters, last_time, quote)
                    values(:channel, :nick,
                        coalesce((select lines from lines_by_nick where
                            channel=:channel and nick=:nick) + 1, 1),
                        coalesce((select characters from lines_by_nick where
                            channel=:channel and nick=:nick) + :chars, :chars),
                        CURRENT_TIMESTAMP, :msg
                    );''', sqlite_data)

        cursor.execute('update lines_by_nick set quote=:msg where channel=:channel and nick=:nick', sqlite_data)

if __name__ == '__main__':
    print(__doc__.strip())
