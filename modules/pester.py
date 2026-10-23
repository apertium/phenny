#!/usr/bin/python3
"""
pester.py - Pester module
Author - mandarj
"""

import os, sqlite3
from datetime import datetime, UTC
from modules import caseless_list
from tools import db_path
from bot import command, every_message

def setup(self):
    self.pester_db = db_path(self, 'pester')
    conn = sqlite3.connect(self.pester_db)

    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS to_pester (pesteree TEXT, pesterer TEXT, reason TEXT, dismissed TEXT, last_pestered TEXT, created TEXT);''')
    conn.commit()
    conn.close()

@command('pester')
def start_pester(phenny, msg):
    '''Start pestering someone. Usage: <bot_nick>: pester <someone> <to do something>'''
    if not msg.command_args:
        return
    conn = sqlite3.connect(phenny.pester_db)
    c = conn.cursor()
    inputnick = msg.nick.casefold()
    pesternick = msg.command_args_list[0].lower()
    text = ''
    if len(msg.command_args_list) > 1:
        text = msg.command_args.split(' ', 1)[1]

    c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', [pesternick, inputnick])
    if c.fetchall() == []:
        current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''INSERT INTO to_pester VALUES(?,?,?,?,?,?);''', [pesternick, inputnick, text, current_time, "", current_time])
        start_pester.conn.commit()
        msg = msg.nick + ": I will start pestering " + msg.command_args_list[0] + " " + text
        phenny.say(msg)
    else:
        phenny.say(msg.nick + ': You are already pestering ' + msg.command_args_list[0])

    conn.commit()
    conn.close()

@every_message
def pester(phenny, msg):
    pester.conn = sqlite3.connect(phenny.pester_db)
    c = pester.conn.cursor()
    inputnick = msg.nick.casefold()

    pesterees = []
    c.execute('''SELECT pesteree FROM to_pester''')
    for name in c.fetchall():
        pesterees.append(name[0].casefold())

    if inputnick in pesterees:
        reasons = []
        c.execute('''SELECT reason FROM to_pester WHERE pesteree=?''',
                [inputnick])
        for reason in c.fetchall():
            reasons.append(reason[0])

        for reason in reasons:
            pesterers = []
            c.execute('''SELECT pesterer FROM to_pester WHERE pesteree=? AND reason=?''', (inputnick, reason))
            for name in c.fetchall():
                pesterers.append(name[0])

            for pesterer in pesterers:
                c.execute('''SELECT dismissed FROM to_pester WHERE pesteree=? AND pesterer=? AND reason=?''', (inputnick, pesterer, reason))
                last_dismissed = c.fetchall()[0][0]
                current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
                c.execute('''SELECT created FROM to_pester WHERE pesteree=? AND pesterer=? AND reason=?''', (inputnick, pesterer, reason))
                created_str = c.fetchall()[0][0]
                if last_dismissed == "":
                    c.execute('''SELECT last_pestered FROM to_pester WHERE pesteree=? AND pesterer=? AND reason=?''', (inputnick, pesterer, reason))
                    last_pester_str = c.fetchall()[0][0]
                    try:
                        last_pestered = datetime.strptime(last_pester_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                    delta = last_pestered - datetime.now(UTC)
                    difference = delta.total_seconds() / 60 # in minutes
                    if abs(difference) > phenny.config.minutes_to_pester:
                        msg = msg.nick + ': (' + created_str + ') ' + pesterer + ' pesters you ' + reason
                        phenny.say(msg)
                        c.execute('''UPDATE to_pester SET last_pestered=? WHERE pesteree=? AND pesterer=? AND reason=?''',
                                (current_time, inputnick, pesterer, reason))
                        pester.conn.commit()
                else:
                    dismissed = datetime.strptime(last_dismissed, "%Y-%m-%d %H:%M:%S")
                    delta = dismissed - datetime.now(UTC)
                    difference = delta.total_seconds() / 60 # in minutes
                    if abs(difference) > phenny.config.pester_after_dismiss:
                        msg = msg.nick + ': (' + created_str + ') ' + pesterer + ' pesters you ' + reason
                        phenny.say(msg)
                        c.execute('''UPDATE to_pester SET last_pestered=? WHERE pesteree=? AND pesterer=? AND reason=?''',
                                (current_time, inputnick, pesterer, reason))
                        c.execute('''UPDATE to_pester SET dismissed=? WHERE pesteree=? AND pesterer=? AND reason=?''', ("", inputnick, pesterer, reason))
                        pester.conn.commit()

def pester_exists(cur, pesteree, pesterer):
    qr = 'SELECT * FROM to_pester WHERE pesteree = ? AND pesterer = ?'
    cur.execute(qr, [pesteree.lower(), pesterer.lower()])
    return cur.fetchall()

def stop_pester(phenny, user, pesteree, pesterer):
    conn = sqlite3.connect(phenny.pester_db)
    cur = conn.cursor()
    if pester_exists(cur, pesteree, pesterer):
        cur.execute('DELETE FROM to_pester WHERE pesteree = ? AND pesterer = ?', (pesteree.lower(), pesterer.lower()))
        phenny.say(user + ': ' + ('You are' if user == pesterer else pesterer + ' is') + ' no longer pestering ' + ('you' if user == pesteree else pesteree) + '.')
        conn.commit()
    else:
        phenny.say(user + ': ' + ('You are' if user == pesterer else pesterer + ' is') + ' not pestering ' + ('you' if user == pesteree else pesteree) + '.')
    conn.close()

@command('pesters')
def pesters(phenny, msg):
    match msg.command_args_list:
        case ['snooze', pesterer]:
            conn = sqlite3.connect(phenny.pester_db)
            cur = conn.cursor()
            if pester_exists(cur, msg.nick, pesterer):
                now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
                cur.execute('UPDATE to_pester SET dismissed = ? WHERE pesteree = ? AND pesterer = ?', [now, msg.nick.lower(), pesterer.lower()])
                phenny.reply(f'Pester snoozed. Pester will recur in {phenny.config.pester_after_dismiss} minutes.')
                conn.commit()
            else:
                phenny.reply(f'You are not being pestered by {pesterer}.')
            conn.close()
        case ['dismiss', 'from', pesterer]:
            stop_pester(phenny, msg.nick, msg.nick, pesterer)
        case ['dismiss', 'to', pesteree]:
            stop_pester(phenny, msg.nick, pesteree, msg.nick)
        case ['remove', 'from', pesterer]:
            stop_pester(phenny, msg.nick, msg.nick, pesterer)
        case ['remove', 'to', pesteree]:
            stop_pester(phenny, msg.nick, pesteree, msg.nick)
        case ['delete', 'from', pesterer]:
            stop_pester(phenny, msg.nick, msg.nick, pesterer)
        case ['delete', 'to', pesteree]:
            stop_pester(phenny, msg.nick, pesteree, msg.nick)
        case ['rm', 'from', pesterer]:
            stop_pester(phenny, msg.nick, msg.nick, pesterer)
        case ['rm', 'to', pesteree]:
            stop_pester(phenny, msg.nick, pesteree, msg.nick)
        case ['del', 'from', pesterer]:
            stop_pester(phenny, msg.nick, msg.nick, pesterer)
        case ['del', 'to', pesteree]:
            stop_pester(phenny, msg.nick, pesteree, msg.nick)
        case ['stop', pesterer, 'to', pesteree]:
            if msg.nick in phenny.config.admins:
                stop_pester(phenny, msg.nick, pesteree, pesterer)
            else:
                phenny.reply('Only admins can stop pesters of other people.')
        case _:
            phenny.reply('Usage: .pesters dismiss|remove|delete|rm|del to|from <user> or .pesters snooze <user> or .pesters stop <user> to <user>')
