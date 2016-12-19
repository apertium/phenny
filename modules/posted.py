#!/usr/bin/python3
"""
posted.py - Remembers who posted which URL, can show on URL match. 
author: andreim <andreim@andreim.net>
"""
import os
import sqlite3
from humanize import naturaltime
import requests

def setup(self):
    fn = self.nick + '-' + self.config.host + '.posted.db'
    self.posted_db = os.path.join(os.path.expanduser('~/.phenny'), fn)
    conn = sqlite3.connect(self.posted_db)

    c = conn.cursor()
    c.execute('''create table if not exists posted (
        channel     varchar(255),
        nick        varchar(255),
        url       varchar(512),
        time   timestamp date default (datetime('now', 'localtime'))
    );''')

    c.close()
    conn.close()


def check_posted(phenny, input, url):
    if url:
        if ':' not in url:
            url = 'http://' + url
        dest_url = requests.get(url).url
        conn = sqlite3.connect(phenny.posted_db, 
            detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("SELECT nick, time FROM posted WHERE channel=? AND url=?", 
            (input.sender, dest_url))
        res = c.fetchone()

        posted = None

        if res:
            nickname = res[0]
            time = naturaltime(res[1])

            posted = "{0} by {1}".format(time, nickname)


        else:
            c.execute("INSERT INTO posted (channel, nick, url) VALUES (?, ?, ?)", 
                (input.sender, input.nick, dest_url))
            conn.commit()

        conn.close()

        return posted


def posted(phenny, input):
    if not input.group(2):
        return phenny.say(".posted <URL> - checks if URL has been posted"
        + " before in this channel.")
    url = input.group(2)

    posted = check_posted(phenny, input, url)
    if posted:
        phenny.reply("URL was posted {0}".format(posted))
    else:
        phenny.reply("I don't remember seeing this URL in this channel.")

posted.thread = False
posted.commands = ["posted"]
