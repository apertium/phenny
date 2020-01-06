#!/usr/bin/python3
"""
pester.py - Pester module
Author - mandarj
"""

import os, sqlite3
from datetime import datetime
from modules import caseless_list
from tools import db_path

def setup(self):
    self.pester_db = db_path(self, 'pester')
    self.pester_conn = sqlite3.connect(self.pester_db)

    c = self.pester_conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS to_pester (pesteree TEXT, pesterer TEXT, reason TEXT, dismissed TEXT, last_pestered TEXT, created TEXT);''')


def start_pester(phenny, input):
    '''Start pestering someone. Usage: <bot_nick>: pester <someone> <to do something>'''
    start_pester.conn = sqlite3.connect(phenny.pester_db)
    c = start_pester.conn.cursor()
    inputnick = input.nick.casefold()
    pesternick = input.group(1).casefold()

    c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', [pesternick, inputnick])
    if c.fetchall() == []:
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''INSERT INTO to_pester VALUES(?,?,?,?,?,?);''', [pesternick, inputnick, input.group(2), current_time, "", current_time])
        start_pester.conn.commit()
        msg = input.nick + ": I will start pestering " + input.group(1) + " " + input.group(2)
        phenny.say(msg)
    else:
        phenny.say(input.nick + ': You are already pestering ' + input.group(1))

    start_pester.conn.commit()
    start_pester.conn.close()
start_pester.name = 'pester'
start_pester.conn = None
start_pester.rule = ('$nick', ['pester'], r'(\S+) (.*)')


def pester(phenny, input):
    pester.conn = sqlite3.connect(phenny.pester_db)
    c = pester.conn.cursor()
    inputnick = input.nick.casefold()

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
                current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                c.execute('''SELECT created FROM to_pester WHERE pesteree=? AND pesterer=? AND reason=?''', (inputnick, pesterer, reason))
                created_str = c.fetchall()[0][0]
                if last_dismissed == "":
                    c.execute('''SELECT last_pestered FROM to_pester WHERE pesteree=? AND pesterer=? AND reason=?''', (inputnick, pesterer, reason))
                    last_pester_str = c.fetchall()[0][0]
                    try:
                        last_pestered = datetime.strptime(last_pester_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                    delta = last_pestered - datetime.utcnow()
                    difference = delta.total_seconds() / 60 # in minutes
                    if abs(difference) > phenny.config.minutes_to_pester:
                        msg = input.nick + ': (' + created_str + ') ' + pesterer + ' pesters you ' + reason
                        phenny.say(msg)
                        c.execute('''UPDATE to_pester SET last_pestered=? WHERE pesteree=? AND pesterer=? AND reason=?''',
                                (current_time, inputnick, pesterer, reason))
                        pester.conn.commit()
                else:
                    dismissed = datetime.strptime(last_dismissed, "%Y-%m-%d %H:%M:%S")
                    delta = dismissed - datetime.utcnow()
                    difference = delta.total_seconds() / 60 # in minutes
                    if abs(difference) > phenny.config.pester_after_dismiss:
                        msg = input.nick + ': (' + created_str + ') ' + pesterer + ' pesters you ' + reason
                        phenny.say(msg)
                        c.execute('''UPDATE to_pester SET last_pestered=? WHERE pesteree=? AND pesterer=? AND reason=?''',
                                (current_time, inputnick, pesterer, reason))
                        c.execute('''UPDATE to_pester SET dismissed=? WHERE pesteree=? AND pesterer=? AND reason=?''', ("", inputnick, pesterer, reason))
                        pester.conn.commit()
    else:
        pass
pester.rule = r'(.*)'

def pesters(phenny, input):
    '''Usage: ".pesters snooze <person pestering you>" to 'snooze' a pester; ".pesters remove <person pestering you>" to stop being pestered by someone; ".pesters dismiss <person you are pestering>" to stop pestering someone.'''
    pesters.conn = sqlite3.connect(phenny.pester_db)
    c = pesters.conn.cursor()
    inputnick = input.nick.casefold()
    pesterernick = input.group(2).casefold()

    if input.group(1) == 'snooze':
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', [inputnick, pesterernick]).fetchall() == []:
            phenny.say(input.nick + ': You are not being pestered by ' + input.group(2))
        else:
            c.execute('''UPDATE to_pester SET dismissed=? WHERE pesteree=? AND pesterer=?''', [current_time, inputnick, pesterernick])
            phenny.say(input.nick + ': Pester snoozed. Pester will recur in ' + str(phenny.config.pester_after_dismiss) + ' minutes.')

    elif input.group(1) == 'remove':
        if c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', [inputnick, pesterernick]).fetchall() == []:
            phenny.say(input.nick + ': You are not being pestered by ' + input.group(2))
        else:
            c.execute('''DELETE FROM to_pester WHERE pesteree=? AND pesterer=?''', [inputnick, pesterernick])
            phenny.say(input.nick + ': You won\'t be pestered by ' + input.group(2) + ' anymore.')

    elif input.group(1) == 'dismiss':
        if c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', [pesterernick, inputnick]).fetchall() == []:
            phenny.say(input.nick + ': You are not pestering ' + input.group(2))
        else:
            c.execute('''DELETE FROM to_pester WHERE pesteree=? AND pesterer=?''', [pesterernick, inputnick])
            phenny.say(input.nick + ': Stopped pestering ' + input.group(2))

    pesters.conn.commit()
pesters.name = 'pesters'
pesters.rule = r'[.]pesters (snooze|dismiss|remove) (\S+)'

def admin_stop(phenny, input):
    '''Usage: ".pesters stop <pesterer> to <pesteree>" to stop a pester from <pesterer> to <pesteree>. This functions is for *admins only*.'''
    admin_stop.conn = sqlite3.connect(phenny.pester_db)
    c = admin_stop.conn.cursor()

    if input.nick.casefold() in caseless_list(phenny.config.admins):
        if c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', (input.group(2).casefold(), input.group(1).casefold())).fetchall == []:
            phenny.say(input.nick + ': ' + input.group(1) + ' is not pestering ' + input.group(2))
        else:
            c.execute('''DELETE FROM to_pester WHERE pesteree=? AND pesterer=?''', (input.group(2).casefold(), input.group(1).casefold()))
            phenny.say(input.nick + ': ' + input.group(1) + ' is no longer pestering ' + input.group(2))
            admin_stop.conn.commit()
    else:
        phenny.say('You need to be admin to perform this function.')
admin_stop.name = 'pester stop'
admin_stop.rule = r'[.]pesters stop (\S+) to (\S+)'
