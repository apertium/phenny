import hashlib
import sqlite3
import time
from tools import DatabaseCursor, db_path

def setup(self):
    # volatile data: nick -> last_time
    # entries exist for as long as nick is active
    self.gci_data = {}

    # persistent data: nick -> mentor_nick, code, all_time
    self.gci_db = db_path(self, 'gci_data')

    connection = sqlite3.connect(self.gci_db)
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS gci_data (
        nick        varchar(255),
        mentor_nick varchar(255),
        code        varchar(255),
        all_time    unsigned big int not null default 0,
        UNIQUE (nick, code) ON CONFLICT REPLACE
    );''')

    cursor.close()
    connection.close()
    
def teardown(self):
    # save active nicks to disk
    for nick in self.gci_data:
        inactivity(self, nick)

def gen_code(nick, mentor_nick):
        m = hashlib.sha256()
        m.update(nick.encode())
        m.update(mentor_nick.encode())
        return m.hexdigest()[:8]        

def select(phenny, nick):
    sqlite_data = {
        'nick': nick
    }

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("SELECT mentor_nick, code, all_time FROM gci_data WHERE nick=:nick", sqlite_data)
        return cursor.fetchone()

def insert(phenny, nick, mentor_nick, code, all_time=0):
    sqlite_data = (nick, mentor_nick, code, all_time)

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("INSERT INTO gci_data (nick, mentor_nick, code, all_time) VALUES (?, ?, ?, ?)", sqlite_data)

def update(phenny, nick, all_time):
    sqlite_data = {
        'nick': nick,
        'all_time': all_time,
    }

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("UPDATE gci_data SET all_time=:all_time WHERE nick=:nick", sqlite_data)

def delete(phenny, nick):
    sqlite_data = {
        'nick': nick
    }

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("DELETE FROM gci_data WHERE nick=:nick", sqlite_data)

def commutate(phenny, nick):
    now_time = time.time()
    last_time = phenny.gci_data[nick]['last_time']
    new_time = now_time - last_time

    mentor_nick, code, all_time = select(phenny, nick)
    all_time += now_time - last_time

    update(phenny, nick, all_time)
    phenny.gci_data[nick]["last_time"] = now_time

    # notify if all_time crossed 4 hours
    if all_time - new_time <= 4*60*60 <= all_time:
        phenny.msg("#apertium", "{} (linked by {}) has stayed on the IRC channel for four hours! Code: {}".format(nick, mentor_nick, code))

def activity(phenny, nick):
    if nick in phenny.gci_data:
        # nick was already active, nothing to do
        return

    if not select(phenny, nick):
        # nick is not linked, don't care
        return

    phenny.gci_data[nick] = {
        "last_time": time.time(),
    }

def inactivity(phenny, nick):
    if nick not in phenny.gci_data:
        # nick was not active, hiccup
        return

    commutate(phenny, nick)
    del phenny.gci_data[nick]

def joining(phenny, input):
    nick = input.nick.casefold()
    activity(phenny, nick)

joining.event = "JOIN"
joining.rule = r'(.*)'

def messaging(phenny, input):
    nick = input.nick.casefold()
    activity(phenny, nick)

    if not phenny.gci_data:
        # no one active (yet), nothing to do
        return

    last_update = time.time() - min(data["last_time"] for (nick, data) in phenny.gci_data.items())

    if last_update < 5*60:
        # already updated in last 5 minutes
        return

    for nick in phenny.gci_data:
        commutate(phenny, nick)

messaging.rule = r'(.*)'

def linking(phenny, input):  
    if not input.group(1):
        phenny.reply("Syntax: .gci <nick>")
        return

    s = select(phenny, nick)
    if not s:
        phenny.reply("{} has already been linked to the GCI module.".format(nick))
        return
    
    mentor_nick = input.nick.casefold()
    nick = input.group(1).casefold()
    code = gen_code(nick, mentor_nick)

    insert(phenny, nick, mentor_nick, code)
    activity(phenny, nick)
    phenny.msg("#apertium", "{} has been linked to the GCI module by {}! Code: {}".format(nick, mentor_nick, code))
    
linking.rule = r'\.gci(?:\s+(.+))'

def checking(phenny, input):
    nick = input.group(1).casefold()

    if not nick:
        phenny.reply("Syntax: .gci_check <nick>")
        return
    
    t = select(phenny, nick)
    if not t:
        phenny.reply("The nick '{}' isn't linked to the GCI module.".format(nick))
        return

    if nick in phenny.gci_data:
        commutate(phenny, nick)
    mentor_nick, code, all_time = t
    phenny.reply("nick: {}, mentor: {}, code: {}, all time: {} s ({:.2f} hrs)"
                 .format(nick, mentor_nick, code, int(all_time), int(all_time) / 3600))

checking.rule = r'\.gci_check(?:\s+(.+))'

def quitting(phenny, input):
    nick = input.nick.casefold()
    inactivity(phenny, nick)

quitting.event = "QUIT"
quitting.rule = r'(.*)'

def parting(phenny, input):
    nick = input.nick.casefold()
    inactivity(phenny, nick)

parting.event = "PART"
parting.rule = r'(.*)'

def kicked(phenny, input):
    nick = input.args[2].casefold()
    inactivity(phenny, nick)

kicked.event = "KICK"
kicked.rule = r'(.*)'

def nickchange(phenny, input):
    old_nick = input.nick.casefold()
    new_nick = input.args[1].casefold()

    t = select(phenny, old_nick)
    if not t:
        # nick not linked, don't care
        return
    mentor_nick, code, all_time = t
    
    inactivity(phenny, old_nick)
    delete(phenny, old_nick)

    insert(phenny, new_nick, mentor_nick, code, all_time)
    activity(phenny, new_nick)
    
    phenny.msg("#apertium", "{} (linked to the GCI module by {}) has been changed to {}. Code: {}".format(old_nick, mentor_nick, new_nick, code))

nickchange.event = "NICK"
nickchange.rule = r'(.*)'
