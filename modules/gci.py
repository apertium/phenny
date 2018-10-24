import sqlite3
import time
from tools import DatabaseCursor, db_path

def setup(self):
    # volatile data: nick -> last_time
    # entries exist for as long as nick is active
    self.gci_data = {}

    # persistent data: nick -> full_name, all_time
    self.gci_db = db_path(self, 'gci')

    connection = sqlite3.connect(self.gci_db)
    cursor = connection.cursor()

    cursor.execute('''create table if not exists gci_data (
        nick        varchar(255),
        full_name   varchar(255),
        all_time    unsigned big int not null default 0,
        unique (nick, full_name) on conflict replace
    );''')

    cursor.close()
    connection.close()

def teardown(self):
    # save active nicks to disc

    for nick in self.gci_data:
        inactivity(self, nick)

def select(phenny, nick):
    sqlite_data = {
        'nick': nick
    }

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("SELECT full_name, all_time FROM gci_data WHERE nick=:nick", sqlite_data)
        return cursor.fetchone()

def insert(phenny, nick, full_name, all_time=0):
    values = (nick, full_name, all_time)

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("INSERT INTO gci_data (nick, full_name, all_time) VALUES (?, ?, ?)", values)

def update(phenny, nick, all_time):
    sqlite_data = {
        'nick': nick,
        'all_time': all_time,
    }

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("UPDATE gci_data set all_time=:all_time where nick=:nick", sqlite_data)

def delete(phenny, nick):
    sqlite_data = {
        'nick': nick
    }

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("DELETE FROM gci_data WHERE nick=:nick", sqlite_data)

def commutate(phenny, nick):
    # all_time (persistent) += now_time - last_time (volatile)
    # last_time = now_time

    now_time = time.time()
    last_time = phenny.gci_data[nick]['last_time']
    new_time = now_time - last_time

    full_name, all_time = select(phenny, nick)
    all_time += new_time

    update(phenny, nick, all_time)
    phenny.gci_data[nick]["last_time"] = now_time

    # notify if all_time crossed 4 hours

    if all_time - new_time <= 4*60*60 <= all_time:
        phenny.msg("#apertium", full_name + " stayed on the IRC channel for four hours.")

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
    nick = input.nick.casefold()
    full_name = input.group(1)

    if not full_name:
        phenny.reply("Syntax: .gci <full_name>")
        return

    insert(phenny, nick, full_name)
    activity(phenny, nick)

linking.rule = r'\.gci(?:\s+(.+))'

def checking(phenny, input):
    nick = input.group(1).casefold()

    if not nick:
        phenny.reply("Syntax: .gci_check <nick>")
        return

    if nick in phenny.gci_data:
        commutate(phenny, nick)

    row = select(phenny, nick)

    if not row:
        phenny.reply("This nick isn't linked")
        return

    full_name, all_time = row
    phenny.reply("nick: %s, full name: %s, all time: %s / 14400 seconds" % (nick, full_name, int(all_time)))

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

    row = select(old_nick)

    if not row:
        # nick not linked, don't care
        return

    full_name, all_time = row

    inactivity(phenny, old_nick)
    delete(phenny, old_nick)

    insert(phenny, new_nick, full_name, all_time)
    activity(phenny, new_nick)

nickchange.event = "NICK"
nickchange.rule = r'(.*)'
