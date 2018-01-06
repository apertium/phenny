#!/usr/bin/python3
"""
posted.py - Remembers who posted which URL, can show on URL match.
author: andreim <andreim@andreim.net>
"""

import sqlite3
from humanize import naturaltime
import requests
from tools import DatabaseCursor, db_path

def setup(self):
    self.posted_db = db_path(self, 'posted')

    connection = sqlite3.connect(self.posted_db)
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS posted (
        channel    VARCHAR(255),
        nick       VARCHAR(255),
        url        VARCHAR(512),
        time       TIMESTAMP DATE DEFAULT (DATETIME('now', 'localtime'))
    );''')

    cursor.close()
    connection.close()

def check_posted(phenny, input, url):
    if not url:
        return None

    if ':' not in url:
        url = 'http://' + url
    dest_url = requests.get(url, timeout=61).url

    with DatabaseCursor(phenny.posted_db) as cursor:
        cursor.execute("SELECT nick, time FROM posted WHERE channel=? AND url=?", (input.sender, dest_url))
        res = cursor.fetchone()

        if res:
            nickname = res[0]
            time = naturaltime(res[1])
            return "{0} by {1}".format(time, nickname)
        else:
            cursor.execute("INSERT INTO posted (channel, nick, url) VALUES (?, ?, ?)",
                      (input.sender, input.nick, dest_url))
            return None

def posted(phenny, input):
    if not input.group(2):
        return phenny.say(".posted <URL> - checks if URL has been posted before in this channel.")

    url = input.group(2)
    posted = check_posted(phenny, input, url)

    if posted:
        phenny.reply("URL was posted {0}".format(posted))
    else:
        phenny.reply("I don't remember seeing this URL in this channel.")

posted.thread = False
posted.commands = ["posted"]
