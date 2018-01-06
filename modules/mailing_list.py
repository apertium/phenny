#!/usr/bin/env python3
"""
mailing_list.py - mailing list reporter
author: mattr555 <mattramina@gmail.com>
"""

import threading
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_tz
import datetime
import re
from tools import truncate
from modules import more
import logging

logger = logging.getLogger('phenny')

def configured(phenny):
    return all(hasattr(phenny.config, i) for i in ['imap_server', 'imap_user', 'imap_pass', 'mailing_lists'])

def setup(phenny):
    if not configured(phenny):
        logger.info("Mailing list configuration not fully defined, aborting.")
        return

    phenny.mailing_list_timer = threading.Timer(60*5, check_mail, (phenny,))
    phenny.mailing_list_timer.start()

def recipients(e):
    s = e.get('From', '') + e.get('To', '') + e.get('CC', '')
    return s

def get_text(e):
    for part in e.walk():
        if part.get_content_maintype() == "text":
            return part.get_payload(decode=True)

def strip_reply_lines(e):
    message = str(get_text(e), encoding='utf8').split('\n')
    stripped = []
    for i in message:
        if i.startswith('>'):
            continue
        stripped.append(i)
    return " ␍ ".join(stripped)

def obfuscate_address(address):
    def first_three_chars(match):
        return match.group(1)[:3] + '...' + match.group(2)[:3] + '...' + match.group(3)
    return re.sub(r'([^\s@]+)(@[-\.\w]+)(\.\w+)', first_three_chars, address)

def login(phenny):
    if not configured(phenny):
        return
    try:
        mail = imaplib.IMAP4_SSL(phenny.config.imap_server)
        mail.login(phenny.config.imap_user, phenny.config.imap_pass)
        return mail
    except imaplib.IMAP4.error:
        phenny.msg(phenny.config.owner, 'IMAP connection/auth failed :(')

def format_email(e, list_name):
    subject = e['Subject']
    subject = re.sub(r"(=\?.*\?=)(?!$)", r"\1 ", subject)
    subject = ''.join([unicode(t[0], t[1] or 'utf-8') for t in decode_header(subject)])
    subject = subject.replace('['+list_name.capitalize()+'] ', '')

    # message = '{}: {} * {} * {}'.format(list_name, obfuscate_address(e['From']), subject, strip_reply_lines(e))
    message = '{}: {}: {}'.format(list_name, obfuscate_address(e['From']), subject)

    return truncate(message)

def check_mail(phenny):
    found = False
    mail = login(phenny)

    if not mail:
        return

    mail.select('inbox')
    rc, data = mail.uid('search', None, 'UNSEEN')
    unseen_mails = data[0].split()

    messages = {}

    for uid in unseen_mails:
        rc, data = mail.uid('fetch', uid, '(RFC822)')
        e = email.message_from_string(data[0][1].decode('utf8'))

        for name, (address, channels) in phenny.config.mailing_lists.items():
            if address in recipients(e):
                found = True
                message = format_email(e, name)

                if type(channels) is str:
                    channels = [channels]

                for channel in channels:
                    if not channel in messages:
                        messages[channel].append(message)
                    else:
                        messages[channel] = [message]

        rc, data = mail.uid('store', uid, '+FLAGS', '(\\Seen)')

    for channel in messages.keys():
        more.add_messages(phenny, 'mailinglist', channel, messages[channel])

    mail.logout()
    phenny.mailing_list_timer = threading.Timer(60*5, check_mail, (phenny,))
    phenny.mailing_list_timer.start()
    return found

def last_message(phenny, ml):
    mail = login(phenny)
    mail.select(ml)
    try:
        uids = mail.uid('search', None, 'ALL')[1][0].decode('utf8').split(' ')
    except imaplib.IMAP4.error:
        return 'A mailing list filter has not been set up for {}, bug {} to fix it'.format(ml, phenny.config.owner)
    best = ('', datetime.datetime(1970, 1, 1))

    for uid in uids:
        try:
            d = mail.uid('fetch', uid, '(BODY[HEADER.FIELDS (DATE)])')[1][0][1]
        except imaplib.IMAP4.error:
            return '{}: No emails'.format(ml)
        d = parsedate_tz(d.decode('utf8').strip('Date: ').strip())
        d = datetime.datetime(*d[:7])
        if d > best[1]:
            best = (uid, d)
    m = mail.uid('fetch', best[0], '(RFC822)')
    e = email.message_from_string(m[1][0][1].decode('utf8'))
    return format_email(e, ml)

syntax = 'Syntax: .{0} poll; .{0} last; .{0} last [{1}]'

def list_report(phenny, input):
    """.mailinglist poll - poll for new mailing list messages
    .mailinglist last <list>? - get the latest message in a list or all lists"""

    if not configured(phenny):
        phenny.reply("I'm not configured for mailing lists, ask {} to set them up.".format(phenny.config.owner))
        return

    valid_syntax = False

    if input.group(2):
        if input.group(2) == "poll":
            phenny.reply('Ok, polling.')

            if not check_mail(phenny):
                phenny.reply('Sorry, no unread mailing list messages.')

            valid_syntax = True
        elif input.group(2) == "last":
            if input.group(3):
                if input.group(3) in phenny.config.mailing_lists:
                    phenny.reply(last_message(phenny, input.group(3)))
                    valid_syntax = True
            else:
                for i in phenny.config.mailing_lists:
                    phenny.reply(last_message(phenny, i))

                valid_syntax = True

    if not valid_syntax:
        phenny.reply(syntax.format(input.group(1), ', '.join(phenny.config.mailing_lists.keys())))

list_report.name = "mailing list reporter"
list_report.rule = r'.(mailinglist|ml)(?:\s(poll|last(?:\s([\w-]+))?))?'
list_report.priority = 'medium'
list_report.thread = True
