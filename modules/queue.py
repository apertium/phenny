"""
.queue - list management
author: mattr555
"""

import random
import logging

from modules import caseless_equal
from modules import more
from tools import GrumbleError, read_db, write_db

logger = logging.getLogger('phenny')

commands = [
    '.queue display <name>?',
    '.queue new <name> <items>',
    '.queue delete <name>',
    '.queue <name> add <items>',
    '.queue <name> swap <item/index1>, <item/index2>',
    '.queue <name> move <source_item/index>, <target_item/index>',
    '.queue <name> replace <item/index>, <new_item>',
    '.queue <name> remove <item>',
    '.queue <name> pop',
    '.queue <name> random',
    '.queue <name> reassign <nick>',
    '.queue <name> rename <new_name>'
]

def setup(phenny):
    try:
        phenny.queue_data = read_db(phenny, 'queue')
    except GrumbleError:
        logger.debug('queue database read failed, initializing data')
        phenny.queue_data = {}

def search_queue(queue, query):
    for i in range(len(queue)):
        if queue[i].lower().startswith(query.lower()):
            return int(i)

    return None

def get_queue(queue_data, queue_name, nick):
    lower_names = {k.casefold(): k for k in queue_data.keys()}

    if queue_name.casefold() in lower_names:
        n = lower_names[queue_name.casefold()]
        return n, queue_data[n]
    elif nick.casefold()  + ':' + queue_name.casefold() in lower_names:
        n = lower_names[nick.casefold() + ':' + queue_name.casefold()]
        return n, queue_data[n]

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

    return matches

def print_queue(queue_name, queue):
    return '[{}] - {}'.format(queue_name,
        ', '.join(queue['queue']) if queue['queue'] else '<empty>')

def get_index(phenny, raw, queue_name, queue):
    try:
        index = int(raw)
    except ValueError:
        index = search_queue(queue['queue'], raw)

        if index is None:
            phenny.reply('{} not found in {}'.format(raw, queue_name))
            raise ValueError

    return index

def get_indices(phenny, raw, queue_name, queue):
    raw = map(lambda x: x.strip(), raw.split(','))
    indices = map(lambda x: get_index(phenny, x, queue_name, queue), raw)
    return tuple(indices)

def queue(phenny, input):
    """.queue- queue management."""

    command = input.group(1).lower()

    if not command:
        phenny.reply('Commands: ' + '; '.join(commands))
        return

    if command == 'display':
        search = input.group(2)

        if not search:
            # there was no queue name given, display all of their names
            if phenny.queue_data:
                phenny.reply('Avaliable queues: ' + ', '.join(sorted(phenny.queue_data.keys())))
            else:
                phenny.reply('There are no queues to display.')
            return

        queue_names = disambiguate_name(phenny.queue_data, search)

        if not queue_names:
            phenny.reply('No queues found.')
            return

        if len(queue_names) == 1:
            # there was only one possible queue
            queue_name = queue_names[0]
            queue = phenny.queue_data[queue_name]
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
            return

        for q in queue_names:
            if caseless_equal(q.split(':')[0], input.nick) and caseless_equal(q[len(input.nick)+1:], search):
                # current user owns queue with exact name
                more.add_messages(phenny, input.sender, print_queue(q, phenny.queue_data[q]))
                return
            elif q[q.find(':')+1:] != search:
                # filter queues with exact name
                queue_names.remove(q)

        if len(queue_names) == 1:
            # only one user owns queue with exact name
            queue_name = queue_names[0]
            queue = phenny.queue_data[queue_name]
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
        else:
            # the name was ambiguous, show a list of queues
            phenny.reply('Did you mean: ' + ', '.join(queue_names) + '?')

    elif command == 'new':
        if not input.group(2):
            phenny.reply('Syntax: .queue new <name> <item1>, <item2> ...')

        queue_name = input.nick + ':' + input.group(2)
        owner = input.nick

        if queue_name in phenny.queue_data:
            phenny.reply('You already have a queue with that name! Pick a new name or delete the old one.')
            return

        if input.group(3):
            queue = input.group(3).split(',')
            queue = list(map(lambda x: x.strip(), queue))
            phenny.queue_data[queue_name] = {'owner': owner, 'queue': queue}
            write_db(phenny, 'queue', phenny.queue_data)
            phenny.reply('Queue {} with items {} created.'.format(
                queue_name, ', '.join(queue)))
        else:
            phenny.queue_data[queue_name] = {'owner': owner, 'queue': []}
            write_db(phenny, 'queue', phenny.queue_data)
            phenny.reply('Empty queue {} created.'.format(queue_name))

    elif command in ['delete', 'remove', 'del', 'rm']:
        if not input.group(2):
            phenny.reply('Syntax: .queue delete <name>')

        queue_name, queue = get_queue(phenny.queue_data, input.group(2), input.nick)

        if not queue_name:
            phenny.reply('That queue wasn\'t found!')
            return

        if not (caseless_equal(input.nick, queue['owner']) or input.admin):
            phenny.reply('You aren\'t authorized to do that!')
            return

        phenny.queue_data.pop(queue_name)
        write_db(phenny, 'queue', phenny.queue_data)
        phenny.reply('Queue {} deleted.'.format(queue_name))

    elif get_queue(phenny.queue_data, input.group(1), input.nick)[0]:
        # queue-specific commands
        command = input.group(2).lower()
        queue_name, queue = get_queue(phenny.queue_data, input.group(1), input.nick)

        if not command:
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
            return

        if command == 'random':
            phenny.reply('%s is the lucky one.' % repr(random.choice(queue['queue'])))
            return

        if not (caseless_equal(queue['owner'], input.nick) or input.admin):
            phenny.reply('You aren\'t the owner of this queue!')
            return

        if command == 'add':
            if not input.group(3):
                phenny.reply('Syntax: .queue <name> add <item1>, <item2> ...')
                return

            new_queue = input.group(3).split(',')
            new_queue = list(map(lambda x: x.strip(), new_queue))
            queue['queue'] += new_queue
            write_db(phenny, 'queue', phenny.queue_data)
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
        elif command == 'swap':
            if not input.group(3):
                phenny.reply('Syntax: .queue <name> swap <index/item1>, <index/item2>')
                return

            try:
                id1, id2 = get_indices(phenny, input.group(3), queue_name, queue)
            except ValueError:
                return

            queue['queue'][id1], queue['queue'][id2] = queue['queue'][id2], queue['queue'][id1]
            write_db(phenny, 'queue', phenny.queue_data)
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
        elif command in ['move', 'mv']:
            if not (input.group(3) and ',' in input.group(3)):
                phenny.reply('Syntax: .queue <name> move <source_index/item>, <target_index/item>')
                return

            try:
                id1, id2 = get_indices(phenny, input.group(3), queue_name, queue)
            except ValueError:
                return

            queue['queue'].insert(id2, queue['queue'].pop(id1))
            write_db(phenny, 'queue', phenny.queue_data)
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
        elif command == 'replace':
            if not (input.group(3) and ',' in input.group(3)):
                phenny.reply('Syntax: .queue <name> replace <index/item>, <new_item>')
                return

            old, new = input.group(3).split(',')
            old = old.strip()

            try:
                old_id = int(old)
            except ValueError:
                old_id = search_queue(queue['queue'], old)
                if old_id is None:
                    phenny.reply('{} not found in {}'.format(old, queue_name))
                    return

            queue['queue'][old_id] = new.strip()
            write_db(phenny, 'queue', phenny.queue_data)
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
        elif command in ['remove', 'delete', 'del', 'rm']:
            if not input.group(3):
                phenny.reply('Syntax: .queue <name> remove <item>')
                return

            item = input.group(3)

            if item in queue['queue']:
                queue['queue'].remove(item)
                write_db(phenny, 'queue', phenny.queue_data)
                more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
            elif search_queue(queue['queue'], item):
                queue['queue'].pop(search_queue(queue['queue'], item))
                write_db(phenny, 'queue', phenny.queue_data)
                more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
            else:
                phenny.reply('{} not found in {}'.format(item, queue_name))
        elif command == 'pop':
            try:
                queue['queue'].pop(0)
                write_db(phenny, 'queue', phenny.queue_data)
                more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
            except IndexError:
                phenny.reply('That queue is already empty.')
        elif command == 'reassign':
            if not input.group(3):
                phenny.reply('Syntax: .queue <name> reassign <nick>')
                return

            phenny.queue_data.pop(queue_name)
            new_owner = input.group(3)
            queue_name = new_owner + queue_name[queue_name.index(':'):]
            phenny.queue_data[queue_name] = {'owner': new_owner, 'queue': queue['queue']}
            write_db(phenny, 'queue', phenny.queue_data)
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
        elif command in ['rename', 'ren']:
            if not input.group(3):
                phenny.reply('Syntax: .queue <name> rename <new_name>')
                return

            phenny.queue_data.pop(queue_name)
            queue_name = queue['owner'] + ':' + input.group(3)
            phenny.queue_data[queue_name] = queue
            write_db(phenny, 'queue', phenny.queue_data)
            more.add_messages(phenny, input.sender, print_queue(queue_name, queue))
    else:
        if input.group(3):
            phenny.reply('That\'s not a command. Commands: ' + '; '.join(commands))
        else:
            phenny.reply('That queue wasn\'t found!')

queue.rule = r'\.queue(?:\s([\w:]+))?(?:\s([\w:]+))?(?:\s(.*))?'
