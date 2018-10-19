import sqlite3
import time
from tools import DatabaseCursor, db_path

def setup(self):
    self.gci_data = {}

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
    with DatabaseCursor(self.gci_db) as cursor:
        cursor.execute("SELECT nick FROM gci_data")

        rows = cursor.fetchall()

    for row in rows:
        nick = row[0]
        stop(self, nick)

def commutate(phenny, nick):
    nick = nick.casefold()

    now_time = time.time()
    last_time = phenny.gci_data[nick]['last_time']
    new_time = now_time - last_time

    sqlite_data = {
        'nick': nick,
    }

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("SELECT full_name, all_time FROM gci_data WHERE nick=:nick", sqlite_data)
        full_name, all_time = cursor.fetchone()

        all_time += new_time
        sqlite_data.update({
            'all_time': all_time,
        })

        cursor.execute('update gci_data set all_time=:all_time where nick=:nick', sqlite_data)

    phenny.gci_data[nick]["last_time"] = now_time

    if all_time - new_time <= 4*60*60 <= all_time:
        phenny.msg("#apertium", full_name + " stayed on the IRC channel for four hours.")

def start(phenny, nick):
    nick = nick.casefold()

    if nick in phenny.gci_data:
        return

    sqlite_data = {
        'nick': nick,
    }

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("SELECT COUNT(*) FROM gci_data WHERE nick=:nick", sqlite_data)

        if not cursor.fetchone()[0]:
            return

    phenny.gci_data[nick] = {
        "last_time": time.time(),
    }

def stop(phenny, nick):
    nick = nick.casefold()

    if nick not in phenny.gci_data:
        return

    commutate(phenny, nick)

    del phenny.gci_data[nick]

def joining(phenny, input):
    start(phenny, input.nick)

joining.event = "JOIN"
joining.rule = r'(.*)'

def messaging(phenny, input):
    start(phenny, input.nick)

    if not phenny.gci_data:
        return

    oldest_time = min([data["last_time"] for (nick, data) in phenny.gci_data.items()])
    now_time = time.time()

    if now_time - oldest_time < 5*60:
        return

    for nick in phenny.gci_data:
        commutate(phenny, nick)

messaging.rule = r'(.*)'

def linking(phenny, input):
    nick = input.nick.casefold()
    full_name = input.group(1)

    if not full_name:
        phenny.reply("Syntax: .gci <full_name>")

    values = (nick, full_name, 0)

    with DatabaseCursor(phenny.gci_db) as cursor:
        cursor.execute("INSERT INTO gci_data (nick, full_name, all_time) VALUES (?, ?, ?)", values)

    start(phenny, nick)

linking.rule = r'\.gci(?:\s+(.*))'

def quitting(phenny, input):
    stop(phenny, input.nick)

quitting.event = "QUIT"
quitting.rule = r'(.*)'

def parting(phenny, input):
    stop(phenny, input.nick)

parting.event = "PART"
parting.rule = r'(.*)'

def kicked(phenny, input):
    stop(phenny, input.args[2])

kicked.event = "KICK"
kicked.rule = r'(.*)'

def nickchange(phenny, input):
    stop(phenny, input.nick)
    start(phenny, input.args[1])

nickchange.event = "NICK"
nickchange.rule = r'(.*)'
