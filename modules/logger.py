#!/usr/bin/python3
"""
logger.py - logger for privacy-protecting IRC stats
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import os
import random
import sqlite3

def setup(self):
    fn = self.nick + '-' + self.config.host + '.logger.db'
    self.logger_db = os.path.join(os.path.expanduser('~/.phenny'), fn)
    self.logger_conn = sqlite3.connect(self.logger_db)

    c = self.logger_conn.cursor()
    c.execute('''create table if not exists lines_by_nick (
        channel     varchar(255),
        nick        varchar(255),
        lines       unsigned big int not null default 0,
        characters  unsigned big int not null default 0,
        last_time   timestamp default CURRENT_TIMESTAMP,
        quote       text,
        unique (channel, nick) on conflict replace
    );''')

def logger(phenny, input):
    if not logger.conn:
        logger.conn = sqlite3.connect(phenny.logger_db)

    sqlite_data = {
        'channel': input.sender,
        'nick': input.nick.casefold(),
        'msg': input.group(1),
        'chars': len(input.group(1)),
    }

    # format action messages
    if sqlite_data['msg'][:8] == '\x01ACTION ':
        sqlite_data['msg'] = '* {0} {1}'.format(sqlite_data['nick'], sqlite_data['msg'][8:-1])

    c = logger.conn.cursor()
    c.execute('''insert or replace into lines_by_nick
                    (channel, nick, lines, characters, last_time, quote)
                    values(
                        :channel,
                        :nick,
                        coalesce((select lines from lines_by_nick where
                            channel=:channel and nick=:nick) + 1, 1),
                        coalesce((select characters from lines_by_nick where
                            channel=:channel and nick=:nick) + :chars, :chars),
                        CURRENT_TIMESTAMP,
                        :msg
                    );''', sqlite_data)
    c.close()

    c = logger.conn.cursor()
    c.execute('update lines_by_nick set quote=:msg where channel=:channel \
                and nick=:nick', sqlite_data)
    c.close()

    logger.conn.commit()
logger.conn = None
logger.priority = 'low'
logger.rule = r'(.*)'
logger.thread = False

if __name__ == '__main__':
    print(__doc__.strip())
