#!/usr/bin/python3
import os, sqlite3
from datetime import datetime

#!/usr/bin/python3

def setup(self):
    fn = self.nick + '-' + self.config.host + '.pester.db'
    self.pester_db = os.path.join(os.path.expanduser('~/.phenny'), fn)
    self.pester_conn = sqlite3.connect(self.pester_db)

    c = self.pester_conn.cursor()
    ### note-for-me: set dismissed to "" if is_dismissed is supposed to be false
    c.execute('''CREATE TABLE IF NOT EXISTS to_pester (
        pesteree TEXT,
        pesterer TEXT,
        reason TEXT,
        last_dismissed TEXT,
        last_pestered TEXT
    );''')


def start_pester(phenny, input):
    start_pester.conn = sqlite3.connect(phenny.pester_db)
    c = start_pester.conn.cursor()

    c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', [input.group(2), input.nick])
    if c.fetchall() == []:
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''INSERT INTO to_pester VALUES(?,?,?,?,?);''', [input.group(2), input.nick, input.group(3), current_time, ""])
        start_pester.conn.commit()
        msg = input.nick + ": I will start pestering " + input.group(2) + " to " + input.group(3)
        phenny.say(msg)
    else:
        phenny.say(input.nick + ': You are already pestering ' + input.group(2))
start_pester.conn = None
pester.rule = ('$nick', ['pester'], r'(\S+) to (.*)')


def pester(phenny, input):
    pester.conn = sqlite3.connect(phenny.pester_db)
    c = pester.conn.cursor()

    pesterees = []
    c.execute('''SELECT pesteree FROM to_pester''')
    for name in c.fetchall():
        pesterees.append(name[0])

    if input.nick in pesterees:
        reasons = []
        c.execute('''SELECT reason FROM to_pester WHERE pesteree=?''',
                input.nick)
        for reason in c.fetchall():
            reasons.append(reason[0])
            
        for reason in reasons:
            pesterers = []
            c.execute('''SELECT pesterer FROM to_pester WHERE pesteree=? AND reason=?''', input.nick, reason)
            for name in c.fetchall():
                pesterers.append(name)
            
            for pesterer in pesterers:
                c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=? AND reason=?''', [input.nick, pesterer, reason])
                row = c.fetchone()
                current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                if row[3] == "":
                    last_pester_str = row[4]
                    try:
                        last_pestered = datetime.strptime(last_pester_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                    delta = last_pestered - datetime.utcnow()
                    difference = delta.total_seconds() / 3600 # in hours
                    if difference > 1:
                        msg = input.nick + ': ' + pesterer + ' pesters you to ' + reason
                        phenny.say(msg)
                        c.execute('''UPDATE to_pester SET last_pestered=? WHERE pesteree=? AND pesterer=? AND reason=?''',
                                [current_time, input.nick, pesterer, reason])
                else:
                    try:
                        last_dismissed = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                    delta = last_dismissed - datetime.utcnow()
                    difference = delta.total_seconds() / 3600
                    if difference > 12:
                        msg = input.nick + ': ' + pesterer + ' pesters you to ' + reason
                        phenny.say(msg)
                        c.execute('''UPDATE to_pester SET last_dismissed=? WHERE pesteree=? AND pesterer=? AND reason=?''',
                                [current_time, input.nick, pesterer, reason])
    else:
        pass
pester.conn = None
pester.rule = r'(.*)'

def pesters(phenny, input):
    pesters.conn = sqlite3.connect(phenny.pester_db)
    c = pesters.conn.cursor()
    if input.group(1) == 'dismiss from':
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', [input.nick, input.group(2)]).fetchall() == []:
            phenny.say(input.nick + ': You are not being pestered by ' + input.group(2))
        else:
            c.execute('''UPDATE to_pester SET last_dismissed=? WHERE pesteree=? AND pesterer=?''', [current_time, input.nick, input.group(2)])
            phenny.say(input.nick + ': Dismissed')
        
    elif input.group(1) == 'stop pestering':
        if c.execute('''SELECT * FROM to_pester WHERE pesteree=? AND pesterer=?''', [input.group(2), input.nick]).fetchall() == []:
            phenny.say(input.nick + ': You are not pestering ' + input.group(2))
        else:
            c.execute('''DELETE FROM to_pester WHERE pesteree=? AND pesterer=?''', [input.group(2), input.nick])
            phenny.say(input.nick + ': I have stopped pestering ' + input.group(2))
pesters.rule = r'[.]pesters (dismiss from|stop pestering) (.*)'
