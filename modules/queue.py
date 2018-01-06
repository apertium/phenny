"""
.queue - list management
author: mattr555
"""

import os
import pickle
import random
from modules import more, caseless_equal
from tools import db_path

commands = '.queue display <name>?; .queue new <name> <items>; .queue delete <name>; .queue <name> add <items>; .queue <name> swap <item/index1>, <item/index2>; .queue <name> move <source_item/index>, <target_item/index>; .queue <name> replace <item/index>, <new_item>; .queue <name> remove <item>; .queue <name> pop; .queue <name> random; .queue <name> reassign <nick>; .queue <name> rename <new_name>'

def filename(self):
    return db_path(self, 'queue')

def write_dict(filename, data):
    with open(filename, 'wb') as f:
        f.write(pickle.dumps(data))

def read_dict(filename):
    data = None
    with open(filename, 'rb') as f:
        data = pickle.loads(f.read())
    return data

def setup(phenny):
    f = filename(phenny)
    if os.path.exists(f):
        phenny.queue_data = read_dict(f)
    else:
        phenny.queue_data = {}

def search_queue(queue, query):
    index = None
    for i in range(len(queue)):
        if queue[i].lower().startswith(query.lower()):
            index = int(i)
            break
    return index

def get_queue(queue_data, queue_name, nick):
    lower_names = {k.casefold(): k for k in queue_data.keys()}
    if queue_name.casefold() in lower_names:
        n = lower_names[queue_name.casefold()]
        return n, queue_data[n]
    elif nick.casefold()  + ':' + queue_name.casefold() in lower_names:
        n = lower_names[nick.casefold() + ':' + queue_name.casefold()]
        return n, queue_data[n]
    else:
        for i in lower_names:
            if caseless_equal(queue_name, i.split(':')[1]):
                n = lower_names[i.casefold()]
                return n, queue_data[n]
    return None, None

def disambiguate_name(queue_data, queue_name):
    matches = []

    for i in queue_data:
        if queue_name == i:
            return i

        if queue_name.casefold() in i.casefold():
            matches.append(i)

    return matches[0] if len(matches) == 1 else matches

def print_queue(queue_name, queue):
    return '[{}]- {}'.format(queue_name,
        ', '.join(queue['queue']) if queue['queue'] else '<empty>')

def queue(phenny, raw):
    """.queue- queue management."""
    if raw.group(1):
        command = raw.group(1)
        if command.lower() == 'display':
            search = raw.group(2)
            if search:
                queue_names = disambiguate_name(phenny.queue_data, search)
                if type(queue_names) is str:
                    #there was only one possible queue
                    more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_names, phenny.queue_data[queue_names]))
                elif len(queue_names) > 0:
                    queue_exact = list(queue_names)
                    for q in queue_names:
                        if caseless_equal(q.split(':')[0], raw.nick) and caseless_equal(q[len(raw.nick)+1:], search):
                            #current user owns queue with exact name
                            more.add_messages(phenny, 'queue', raw.nick, print_queue(q, phenny.queue_data[q]))
                            return
                        elif q[q.find(':')+1:] != search:
                            #filter queues with exact name
                            queue_exact.remove(q)
                    if len(queue_exact) == 1:
                        #only one user owns queue with exact name
                        more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_exact[0], phenny.queue_data[queue_exact[0]]))
                    elif len(queue_exact) > 1:
                        #more users own queues with exact name
                        phenny.reply('Did you mean: ' + ', '.join(queue_exact) + '?')
                    else:
                        #the name was ambiguous, show a list of queues
                        phenny.reply('Did you mean: ' + ', '.join(queue_names) + '?')
                else:
                    phenny.reply('No queues found.')
            else:
                #there was no queue name given, display all of their names
                if phenny.queue_data:
                    phenny.reply('Avaliable queues: ' + ', '.join(sorted(phenny.queue_data.keys())))
                else:
                    phenny.reply('There are no queues to display.')

        elif command.lower() == 'new':
            if raw.group(2):
                queue_name = raw.nick + ':' + raw.group(2)
                owner = raw.nick
                if queue_name not in phenny.queue_data:
                    if raw.group(3):
                        queue = raw.group(3).split(',')
                        queue = list(map(lambda x: x.strip(), queue))
                        phenny.queue_data[queue_name] = {'owner': owner, 'queue': queue}
                        write_dict(filename(phenny), phenny.queue_data)
                        phenny.reply('Queue {} with items {} created.'.format(
                            queue_name, ', '.join(queue)))
                    else:
                        phenny.queue_data[queue_name] = {'owner': owner, 'queue': []}
                        write_dict(filename(phenny), phenny.queue_data)
                        phenny.reply('Empty queue {} created.'.format(queue_name))
                else:
                    phenny.reply('You already have a queue with that name! Pick a new name or delete the old one.')
            else:
                phenny.reply('Syntax: .queue new <name> <item1>, <item2> ...')

        elif command.lower() in ['delete', 'remove', 'del', 'rm']:
            if raw.group(2):
                queue_name, queue = get_queue(phenny.queue_data, raw.group(2), raw.nick)
                if type(queue_name) is str:
                    if caseless_equal(raw.nick, queue['owner']) or raw.admin:
                        phenny.queue_data.pop(queue_name)
                        write_dict(filename(phenny), phenny.queue_data)
                        phenny.reply('Queue {} deleted.'.format(queue_name))
                    else:
                        phenny.reply('You aren\'t authorized to do that!')
                else:
                    phenny.reply('That queue wasn\'t found!')
            else:
                phenny.reply('Syntax: .queue delete <name>')

        elif get_queue(phenny.queue_data, raw.group(1), raw.nick)[0]:
            #queue-specific commands
            queue_name, queue = get_queue(phenny.queue_data, raw.group(1), raw.nick)
            if raw.group(2):
                command = raw.group(2).lower()
                if caseless_equal(queue['owner'], raw.nick) or raw.admin:
                    if command == 'add':
                        if raw.group(3):
                            new_queue = raw.group(3).split(',')
                            new_queue = list(map(lambda x: x.strip(), new_queue))
                            queue['queue'] += new_queue
                            write_dict(filename(phenny), phenny.queue_data)
                            more.add_messages(raw.nick.lower(), phenny, print_queue(queue_name, queue))
                        else:
                            phenny.reply('Syntax: .queue <name> add <item1>, <item2> ...')
                    elif command == 'swap':
                        if raw.group(3):
                            indices = raw.group(3).split(',')
                            try:
                                id1, id2 = tuple(map(lambda x: int(x.strip()), indices))[:2]
                            except ValueError:
                                q1, q2 = tuple(map(lambda x: x.strip(), indices))[:2]
                                id1 = search_queue(queue['queue'], q1)
                                if id1 is None:
                                    phenny.reply('{} not found in {}'.format(indices[0].strip(), queue_name))
                                    return
                                id2 = search_queue(queue['queue'], q2)
                                if id2 is None:
                                    phenny.reply('{} not found in {}'.format(indices[1].strip(), queue_name))
                                    return
                            queue['queue'][id1], queue['queue'][id2] = queue['queue'][id2], queue['queue'][id1]
                            write_dict(filename(phenny), phenny.queue_data)
                            more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_name, queue))
                        else:
                            phenny.reply('Syntax: .queue <name> swap <index/item1>, <index/item2>')
                    elif command in ['move', 'mv']:
                        if raw.group(3) and ',' in raw.group(3):
                            indices = raw.group(3).split(',')
                            try:
                                id1, id2 = tuple(map(lambda x: int(x.strip()), indices))[:2]
                            except ValueError:
                                q1, q2 = tuple(map(lambda x: x.strip(), indices))[:2]
                                id1 = search_queue(queue['queue'], q1)
                                if id1 is None:
                                    phenny.reply('{} not found in {}'.format(indices[0].strip(), queue_name))
                                    return
                                id2 = search_queue(queue['queue'], q2)
                                if id2 is None:
                                    phenny,reply('{} not found in {}'.format(indices[1].strip(), queue_name))
                                    return
                            #queue['queue'][id2 + (-1 if id1 < id2 else 0)] = queue['queue'].pop(id1)
                            queue['queue'].insert(id2, queue['queue'].pop(id1))
                            write_dict(filename(phenny), phenny.queue_data)
                            more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_name, queue))
                        else:
                            phenny.reply('Syntax: .queue <name> move <source_index/item>, <target_index/item>')
                    elif command == 'replace':
                        if raw.group(3) and ',' in raw.group(3):
                            old, new = raw.group(3).split(',')
                            old = old.strip()
                            try:
                                old_id = int(old)
                            except ValueError:
                                old_id = search_queue(queue['queue'], old)
                                if old_id is None:
                                    phenny.reply('{} not found in {}'.format(old, queue_name))
                                    return
                            queue['queue'][old_id] = new.strip()
                            write_dict(filename(phenny), phenny.queue_data)
                            more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_name, queue))
                        else:
                            phenny.reply('Syntax: .queue <name> replace <index/item>, <new_item>')
                    elif command in ['remove', 'delete', 'del', 'rm']:
                        if raw.group(3):
                            item = raw.group(3)
                            if item in queue['queue']:
                                queue['queue'].remove(item)
                                write_dict(filename(phenny), phenny.queue_data)
                                more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_name, queue))
                            elif search_queue(queue['queue'], item):
                                queue['queue'].pop(search_queue(queue['queue'], item))
                                write_dict(filename(phenny), phenny.queue_data)
                                more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_name, queue))
                            else:
                                phenny.reply('{} not found in {}'.format(item, queue_name))
                        else:
                            phenny.reply('Syntax: .queue <name> remove <item>')
                    elif command == 'pop':
                        try:
                            queue['queue'].pop(0)
                            write_dict(filename(phenny), phenny.queue_data)
                            more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_name, queue))
                        except IndexError:
                            phenny.reply('That queue is already empty.')
                    elif command == 'random':
                        mphenny.reply('%s is the lucky one.' % repr(random.choice(queue['queue'])))
                    elif command == 'reassign':
                        if raw.group(3):
                            new_owner = raw.group(3)
                            new_queue_name = new_owner + queue_name[queue_name.index(':'):]
                            phenny.queue_data.pop(queue_name)
                            phenny.queue_data[new_queue_name] = {'owner': new_owner, 'queue': queue['queue']}
                            write_dict(filename(phenny), phenny.queue_data)
                            more.add_messages(phenny, 'queue', raw.nick, print_queue(new_queue_name, queue))
                        else:
                            phenny.reply('Syntax: .queue <name> reassign <nick>')
                    elif command.lower() in ['rename', 'ren']:
                        if raw.group(3):
                            new_queue_name = queue['owner'] + ':' + raw.group(3)
                            phenny.queue_data[new_queue_name] = phenny.queue_data.pop(queue_name)
                            write_dict(filename(phenny), phenny.queue_data)
                            more.add_messages(phenny, 'queue', raw.nick, print_queue(new_queue_name, queue))
                        else:
                            phenny.reply('Syntax: .queue <name> rename <new_name>')
                elif command == 'random':
                    phenny.reply('%s is the lucky one.' % repr(random.choice(queue['queue'])))
                else:
                    phenny.reply('You aren\'t the owner of this queue!')
            else:
                more.add_messages(phenny, 'queue', raw.nick, print_queue(queue_name, queue))
        else:
            if raw.group(3):
                phenny.reply('That\'s not a command. Commands: ' + commands)
            else:
                phenny.reply('That queue wasn\'t found!')
    else:
        phenny.reply('Commands: ' + commands)

queue.rule = r'\.queue(?:\s([\w:]+))?(?:\s([\w:]+))?(?:\s(.*))?'
