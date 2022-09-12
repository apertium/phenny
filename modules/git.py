#!/usr/bin/env python
"""
git.py - Github Post-Receive Hooks Module
"""

import atexit
from fnmatch import fnmatch
import http.server
from io import StringIO
import json
import logging
import os
import re
import signal
from threading import Lock, Thread
import time
import urllib.parse

from modules import more
from tools import generate_report, PortReuseTCPServer, truncate
import web

logger = logging.getLogger('phenny')

# githooks port
PORT = 1234

# module-global variables
httpd = None
thread = None
lock = Lock()


def close_socket():
    global httpd, thread

    with lock:
        if httpd:
            httpd.shutdown()
            httpd.server_close()
            httpd = None

        if thread:
            thread.join()
            thread = None

        MyHandler.phenny = None

atexit.register(close_socket)

def signal_handler(signal, frame):
    close_socket()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# githooks handler
class MyHandler(http.server.SimpleHTTPRequestHandler):
    phenny = None

    def return_data(self, site, data, commit):
        '''Generates a report for the specified site and commit.'''

        # fields = project name, author, commit message, modified files, added
        #          files, removed files, revision
        fields = []
        if site == "github":
            fields = [
                data['repository']['name'],
                data['pusher']['name'],
                commit['message'],
                commit['modified'],
                commit['added'],
                commit['removed'],
                commit['id'][:7],
            ]
        elif site == "googlecode":
            fields = [
                data['project_name'],
                commit['author'],
                commit['message'],
                commit['modified'],
                commit['added'],
                commit['removed'],
                commit['revision'],
            ]
        elif site == "bitbucket":
            files = self.getBBFiles(commit['files'])
            fields = [
                'turkiccorpora',
                commit['author'],
                commit['message'],
                files['modified'],
                files['added'],
                files['removed'],
                commit['node'],
            ]
        # the * is for unpacking
        return generate_report(*fields)

    # return error code because a GET request is meaningless
    def do_GET(self):
        parsed_params = urllib.parse.urlparse(self.path)
        query_parsed = urllib.parse.parse_qs(parsed_params.query)
        self.send_response(405)
        self.end_headers()

    def do_POST(self):
        '''Handles POST requests for all hooks.'''
        receive_time = time.time()

        try:
            # read and decode data
            logger.debug('payload received; headers: '+str(self.headers))
            length = int(self.headers['Content-Length'])
            indata = self.rfile.read(length)
            post_data = urllib.parse.parse_qs(indata.decode('utf-8'))

            if len(post_data) == 0:
                post_data = indata.decode('utf-8')
            if "payload" in post_data:
                data = json.loads(post_data['payload'][0])
            else:
                data = json.loads(post_data)
        except Exception as error:
            logger.error('Error 400 (no valid payload)')
            logger.error(str(error))

            # 400 Bad Request
            self.send_response(400)
            self.end_headers()

            for channel in self.phenny.config.channels:
                self.phenny.msg(channel, 'Webhook received malformed payload')

            return

        try:
            result = self.do_POST_unsafe(data)
        except Exception as error:
            logger.error(str(error))
            result = None

        if result:
            status = 200 # OK
        else:
            status = 500 # Internal Server Error

        self.send_response(status)
        self.end_headers()
        self.finish()
        self.connection.close()

        send_time = time.time()
        respond_time = send_time - receive_time
        logger.debug("responded '{:}' in {:.2f}s".format(status, respond_time))

        if result:
            # post all messages to all channels
            channels, messages = result

            for channel in channels:
                more.add_messages(self.phenny, channel, messages)

            return

        logger.error(str(data))

        try:
            commits = [commit['url'] for commit in data['commits']]
            logger.error('Internal Error (commits were ' + ', '.join(commits) + ')')
        except:
            logger.error('Internal Error (commits unknown or malformed)')

        for channel in self.phenny.config.channels:
            self.phenny.msg(channel, 'Webhook received problematic payload')

    def do_POST_unsafe(self, data):
        '''Runs once per event. One repository. One event type.'''
        config = self.phenny.config

        default_channels = config.git_channels.get('*', config.channels)
        channels = default_channels

        # both commit reports and error reports
        messages = []

        repo = ''
        event = None

        # handle GitHub triggers
        if 'GitHub' in self.headers['User-Agent']:
            event = self.headers['X-Github-Event']
            user = data['sender']['login']

            if 'repository' in data:
                repo = data['repository']['name']
            elif 'organization' in data:
                repo = data['organization']['login'] + ' (org)'

            if config.git_events:
                full_name = data['repository']['full_name']
                event_types = []

                for key, value in config.git_events.items():
                    if fnmatch(full_name, key):
                        event_types = value
            else:
                event_types = None

            event_in_config = False
            if 'action' in data:
                for event_type in event_types:
                    if (event + '_' + data['action'] == event_type) or (event == event_type):
                        event_in_config = True

            if (event_types is not None) and ((event not in event_types) and (not event_in_config)):
                return [], []

            if config.git_channels:
                full_name = data['repository']['full_name']
                channels = []

                for key, value in config.git_channels.items():
                    if fnmatch(full_name, key):
                        channels = value

            if event == 'commit_comment':
                commit = data['comment']['commit_id'][:7]
                url = data['comment']['html_url']
                url = url[:url.rfind('/') + 7]
                action = data['action']

                if action == 'deleted':
                    template = '{:}: {:} * comment deleted on commit {:}: {:}'
                    messages.append(template.format(repo, user, commit, url))
                else:
                    template = '{:}: {:} * comment {:} on commit {:}: {:} {:}'
                    messages.append(truncate(
                        data['comment']['body'],
                        template.format(repo, user, action, commit, '{}', url)
                    ))
            elif event == 'create' or event == 'delete':
                template = '{:}: {:} * {:} {:} {:}d {:}'
                ref = data['ref']
                type_ = data['ref_type']
                messages.append(template.format(repo, user, type_, ref, event))
            elif event == 'fork':
                template = '{:}: {:} forked this repo {:}'
                url = data['forkee']['html_url']
                messages.append(template.format(repo, user, url))
            elif event == 'issue_comment':
                if 'pull_request' in data['issue']:
                    url = data['issue']['pull_request']['html_url']
                    text = 'pull request'
                else:
                    url = data['issue']['html_url']
                    text = 'issue'

                number = data['issue']['number']
                action = data['action']

                if action == 'deleted':
                    template = '{:}: {:} * comment deleted on {:} #{:}: {:}'
                    messages.append(template.format(repo, user, text, number, url))
                else:
                    template = '{:}: {:} * comment {:} on {:} #{:}: {:} {:}'
                    messages.append(truncate(
                        data['comment']['body'],
                        template.format(repo, user, action, text, number, '{}', url)
                    ))
            elif event == 'issues':
                template = '{:}: {:} * issue #{:} "{:}" {:} {:} {:}'

                number = data['issue']['number']
                title = data['issue']['title']
                action = data['action']
                url = data['issue']['html_url']
                opt = ''

                if data['issue']['assignee']:
                    opt += 'assigned to ' + data['issue']['assignee']['login']
                elif 'label' in data:
                    opt += 'with ' + data['label']['name']

                messages.append(template.format(repo, user, number, title, action, opt, url))
            elif event == 'member':
                template = '{:}: {:} * user {:} {:} as collaborator {:}'
                new_user = data['member']['login']
                action = data['action']
                messages.append(template.format(repo, user, new_user, action))
            elif event == 'membership':
                template = '{:}: user {:} {:} {:} {:} {:} {:}'
                new_user = data['member']['login']
                action = data['action']
                prep = ['to', 'from'][int(action == 'removed')]
                scope = data['scope']
                name = data['team']['name']
                messages.append(template.format(repo, new_user, action, prep, scope, name))
            elif event == 'pull_request':
                template = '{:}: {:} * pull request #{:} "{:}" {:} {:} {:}'
                number = data['number']
                title = data['pull_request']['title']
                action = data['action']
                url = data['pull_request']['html_url']
                opt = ''

                if data['pull_request']['assignee']:
                    opt = 'to ' + data['pull_request']['assignee']

                messages.append(template.format(repo, user, number, title, action, opt, url))
            elif event == 'pull_request_review_comment':
                template = '{:}: {:} * review comment deleted on pull request #{:}: {:}'
                number = data['pull_request']['number']
                url = data['comment']['html_url']
                action = data['action']
                if action == 'deleted':
                    messages.append(template.format(repo, user, number, url))
                else:
                    template = '{:}: {:} * review comment {:} on pull request #{:}: {:} {:}'
                    try:
                        blacklist_pull_request_comment_users = config.blacklist_pull_request_comment_users
                    except AttributeError:
                        blacklist_pull_request_comment_users = ()
                    if user not in blacklist_pull_request_users:
                        messages.append(truncate(
                            data['comment']['body'],
                            template.format(repo, user, action, number, '{}', url)
                        ))
            elif event == 'push':
                pusher_name = data['pusher']['name']

                if pusher_name in config.gitbots:
                    return [], []

                ref = data['ref'].split('/')[-1]
                repo_fullname = data['repository']['full_name']
                fork = data['repository']['fork']

                if (ref != 'master' and ref != 'main') or fork:
                    try:
                        channels = config.branch_channels[repo_fullname][ref]
                    except:
                        return [], []

                template = '{:}: {:} [ {:} ] {:}: {:}'

                out_messages = []
                out_commithashes = []
                out_files = set()

                for commit in data['commits']:
                    out_commithashes.append(commit['id'][:7])
                    out_files.update(commit['modified'], commit['added'])
                    out_messages.append(commit['message'])

                messages.append(truncate(" * ".join(out_messages), template.format(
                    data['repository']['name'],
                    pusher_name,
                    ' '.join(out_commithashes),
                    ', '.join(out_files),
                    '{}'
                )))

            elif event == 'release':
                template = '{:}: {:} * release {:} {:} {:}'
                tag = data['release']['tag_name']
                action = data['action']
                url = data['release']['html_url']
                messages.append(template.format(repo, user, tag, action, url))
            elif event == 'repository':
                template = 'new repository {:} {:} by {:} {:}'
                name = data['repository']['name']
                action = data['action']
                url = data['repository']['url']
                messages.append(template.format(name, action, user, url, url))
            elif event == 'team_add':
                template = 'repository {:} added to team {:} {:}'
                name = data['repository']['full_name']
                team = data['team']['name']
                messages.append(template.format(name, team))
            elif event == 'ping':
                template = 'ping from {:}, org: {:}'

                if 'organization' in data:
                    org = data['organization']
                else:
                    org = "no org specified!"

                sender = data['sender']['login']
                messages.append(template.format(sender, org))

        elif 'Jenkins' in self.headers['User-Agent']:
            messages.append('Jenkins: {}'.format(data['message']))
        # not github or Jenkins
        elif "commits" in data:
            for commit in data['commits']:
                try:
                    if "author" in commit:
                        # for bitbucket
                        message = self.return_data("bitbucket", data, commit)
                        messages.append(message)
                    else:
                        # we don't know which site
                        message = "unsupported data: " + str(commit)
                        messages.append(message)
                except Exception:
                    logger.warning("unsupported data: " + str(commit))

        if not messages:
            # we couldn't get anything
            channels = default_channels

            if event:
                messages.append("Don't know about '" + event + "' events")
            else:
                messages.append("Unable to deal with unknown event")

        return channels, messages

    def getBBFiles(self, filelist):
        '''Sort filelist into added, modified, and removed files
        (only for bitbucket).'''

        toReturn = {"added": [], "modified": [], "removed": []}
        for onefile in filelist:
            toReturn[onefile['type']].append(onefile['file'])
        return toReturn


def setup_server(phenny):
    '''Set up and start hooks server.'''

    global httpd, thread

    with lock:
        if httpd:
            return

        MyHandler.phenny = phenny
        httpd = PortReuseTCPServer(("", PORT), MyHandler)
        thread = Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()


def auto_start(phenny, input):
    if input.nick != phenny.nick:
        return

    if phenny.config.githook_autostart:
        setup_server(phenny)
auto_start.rule = '(.*)'
auto_start.event = 'JOIN'
auto_start.thread = False

def manual_start(phenny, input):
    phenny.reply("gonna try to setup_server and see if it crashes")
    phenny.teardown()
    setup_server(phenny)

manual_start.name = "manual_start"
manual_start.rule = ".manualstart"
manual_start.thread = False


def teardown(phenny):
    phenny.say("TEARING DOWN SERVER!")
    lock.release()
    thread.stop()
    close_socket()


def gitserver(phenny, input):
    '''Control git server. Possible commands are:
        .gitserver status (all users)
        .gitserver start (admins only)
        .gitserver stop (admins only)'''

    global httpd

    command = input.group(1).strip()
    if input.admin:
        # we're admin
        # everwhere below, 'httpd' being None indicates that the server is not
        # running at the moment
        if command == "stop":
            if httpd is not None:
                teardown(phenny)
            else:
                phenny.reply("Server is already down!")
        elif command == "start":
            if httpd is None:
                setup_server(phenny)
            else:
                phenny.reply("Server is already up!")
        elif command == "status":
            if httpd is None:
                phenny.reply("Server is down! Start using '.gitserver start'")
            else:
                phenny.reply("Server is up! Stop using '.gitserver stop'")
        else:
            phenny.reply("Usage '.gitserver [status | start | stop]'")
    else:
        if command == "status":
            if httpd is None:
                phenny.reply("Server is down! (Only admins can start it up)")
            else:
                phenny.reply(("Server is up and running! "
                             "(Only admins can shut it down)"))
        else:
            phenny.reply("Usage '.gitserver [status]'")
# command metadata and invocation
gitserver.name = "gitserver"
gitserver.rule = ('.gitserver', '(.*)')
gitserver.thread = False


def to_commit(phenny, input):
    api = "https://api.github.com/search/commits?q=%s"
    # currently experimental API
    headers = { "Accept": "application/vnd.github.cloak-preview" }

    sha = input.group(1)
    commit_json = web.get(api % sha, headers=headers)
    data = json.loads(commit_json)

    item = data["items"][0]
    html_url = item["html_url"]

    phenny.reply(html_url)
to_commit.name = "to_commit"
to_commit.rule = '!commit ([0-9a-f]{7,40})'


def get_commit_info(phenny, repo, sha):
    '''Get commit information for a given repository and commit identifier.'''

    repoUrl = phenny.config.git_repositories[repo]
    if repoUrl.find("code.google.com") >= 0:
        locationurl = '/source/detail?r=%s'
    elif repoUrl.find("api.github.com") >= 0:
        locationurl = '/commits/%s'
    elif repoUrl.find("bitbucket.org") >= 0:
        locationurl = ''
    html = web.get(repoUrl + locationurl % sha)
    # get data
    data = json.loads(html)
    author = data['commit']['committer']['name']
    comment = data['commit']['message']

    # create summary of commit
    modified_paths = []
    added_paths = []
    removed_paths = []
    for file in data['files']:
        if file['status'] == 'modified':
            modified_paths.append(file['filename'])
        elif file['status'] == 'added':
            added_paths.append(file['filename'])
        elif file['status'] == 'removed':
            removed_paths.append(file['filename'])
    # revision number is first seven characters of commit indentifier
    rev = sha[:7]
    # format date
    date = time.strptime(data['commit']['committer']['date'],
                         "%Y-%m-%dT%H:%M:%SZ")
    date = time.strftime("%d %b %Y %H:%M:%S", date)

    url = data['html_url']

    return (author, comment, modified_paths, added_paths, removed_paths,
            rev, date), url


def get_recent_commit(phenny, input):
    '''Get recent commit information for each repository Begiak monitors. This
    command is called as 'begiak: recent'.'''

    for repo in phenny.config.git_repositories:
        html = web.get(phenny.config.git_repositories[repo] + '/commits')
        data = json.loads(html)
        # the * is for unpacking
        info, url = get_commit_info(phenny, repo, data[0]['sha'])
        msg = generate_report(repo, *info)
        # the URL is truncated so that it has at least 6 sha characters
        url = url[:url.rfind('/') + 7]
        phenny.say(truncate(msg, '{} ' + url))
# command metadata and invocation
get_recent_commit.rule = ('$nick', 'recent')
get_recent_commit.priority = 'medium'
get_recent_commit.thread = True


def retrieve_commit(phenny, input):
    '''Retreive commit information for a given repository and revision. This
    command is called as 'begiak: info <repo> <rev>'.'''

    # get repo and rev with regex
    data = input.group(1).split(' ')

    if len(data) != 2:
        phenny.reply("Invalid number of parameters.")
        return

    repo = data[0]
    rev = data[1]

    if repo in phenny.config.svn_repositories:
        # we don't handle SVN; see modules/svnpoller.py for that
        return
    if repo not in phenny.config.git_repositories:
        phenny.reply("That repository is not monitored by me!")
        return
    try:
        info, url = get_commit_info(phenny, repo, rev)
    except:
        phenny.reply("Invalid revision value!")
        return
    # the * is for unpacking
    msg = generate_report(repo, *info)
    # the URL is truncated so that it has at least 6 sha characters
    url = url[:url.rfind('/') + 7]
    phenny.say(truncate(msg, '{} ' + url))
# command metadata and invocation
retrieve_commit.rule = ('$nick', 'info(?: +(.*))')
