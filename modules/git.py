#!/usr/bin/env python
"""
git.py - Github Post-Receive Hooks Module
"""

import http.server
from threading import Thread
from io import StringIO
import json
import os
import re
import time
import atexit
import signal
from tools import generate_report, PortReuseTCPServer, truncate
import urllib.parse
import web
from modules import more
import logging

logger = logging.getLogger('phenny')

# githooks port
PORT = 1234

# module-global variables
httpd = None


def close_socket():
    global httpd

    if httpd:
        httpd.shutdown()
        httpd.server_close()

    httpd = None

atexit.register(close_socket)

def signal_handler(signal, frame):
    close_socket()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def setup(phenny):
    if phenny.config.githook_autostart:
        setup_server(phenny)


# githooks handler
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, phenny):
        self.phenny = phenny

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
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        '''Handles POST requests for all hooks.'''

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

            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            for channel in self.phenny.config.channels:
                self.phenny.msg(channel, 'Webhook received malformed payload')

            return

        try:
            self.do_POST_unsafe(data)
        except Exception as error:
            try:
                commits = [commit['url'] for commit in data['commits']]
                logger.error('Error 501 (commits were ' + ', '.join(commits) + ')')
            except:
                logger.error('Error 501 (commits unknown or malformed)')

            logger.error(str(data))
            logger.error(str(error))

            self.send_response(501)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            for channel in self.phenny.config.channels:
                self.phenny.msg(channel, 'Webhook received problematic payload')

    def do_POST_unsafe(self, data):
        # will contain both commit reports and error reports
        msgs_by_channel = {}
        msgs_default_channels = []

        repo = ''
        event = None

        silent_on_purpose = False

        # handle GitHub triggers
        if 'GitHub' in self.headers['User-Agent']:
            event = self.headers['X-Github-Event']
            user = data['sender']['login']

            if 'repository' in data:
                repo = data['repository']['name']
            elif 'organization' in data:
                repo = data['organization']['login'] + ' (org)'

            if event == 'commit_comment':
                commit = data['comment']['commit_id'][:7]
                url = data['comment']['html_url']
                url = url[:url.rfind('/') + 7]
                action = data['action']

                if action == 'deleted':
                    template = '{:}: {:} * comment deleted on commit {:}: {:}'
                    msgs_default_channels.append(template.format(repo, user, commit, url))
                else:
                    template = '{:}: {:} * comment {:} on commit {:}: {:} {:}'
                    comment = truncate(
                        data['comment']['body'],
                        template.format(repo, user, action, commit, '', url)
                    )
                    msgs_default_channels.append(template.format(repo, user, action, commit, comment, url))
            elif event == 'create' or event == 'delete':
                template = '{:}: {:} * {:} {:} {:}d {:}'
                ref = data['ref']
                type_ = data['ref_type']
                msgs_default_channels.append(template.format(repo, user, type_, ref, event))
            elif event == 'fork':
                template = '{:}: {:} forked this repo {:}'
                url = data['forkee']['html_url']
                msgs_default_channels.append(template.format(repo, user, url))
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
                    msgs_default_channels.append(template.format(repo, user, text, number, url))
                else:
                    template = '{:}: {:} * comment {:} on {:} #{:}: {:} {:}'
                    comment = truncate(
                        data['comment']['body'],
                        template.format(repo, user, action, text, number, '', url)
                    )
                    msgs_default_channels.append(template.format(repo, user, action, text, number, comment, url))
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

                msgs_default_channels.append(template.format(repo, user, number, title, action, opt, url))
            elif event == 'member':
                template = '{:}: {:} * user {:} {:} as collaborator {:}'
                new_user = data['member']['login']
                action = data['action']
                msgs_default_channels.append(template.format(repo, user, new_user, action))
            elif event == 'membership':
                template = '{:}: user {:} {:} {:} {:} {:} {:}'
                new_user = data['member']['login']
                action = data['action']
                prep = ['to', 'from'][int(action == 'removed')]
                scope = data['scope']
                name = data['team']['name']
                msgs_default_channels.append(template.format(repo, new_user, action, prep, scope, name))
            elif event == 'pull_request':
                template = '{:}: {:} * pull request #{:} "{:}" {:} {:} {:}'
                number = data['number']
                title = data['pull_request']['title']
                action = data['action']
                url = data['pull_request']['html_url']
                opt = ''

                if data['pull_request']['assignee']:
                    opt = 'to ' + data['pull_request']['assignee']

                msgs_default_channels.append(template.format(repo, user, number, title, action, opt, url))
            elif event == 'pull_request_review_comment':
                template = '{:}: {:} * review comment deleted on pull request #{:}: {:}'
                number = data['pull_request']['number']
                url = data['comment']['html_url']
                action = data['action']

                if action == 'deleted':
                    msgs_default_channels.append(template.format(repo, user, number, url))
                else:
                    template = '{:}: {:} * review comment {:} on pull request #{:}: {:} {:}'
                    comment = truncate(
                        data['comment']['body'],
                        template.format(repo, user, action, number, '', url)
                    )
                    msgs_default_channels.append(template.format(repo, user, action, number, comment, url))
            elif event == 'push':
                template = '{:}: {:} * {:}: {:} {:}'
                ref = data['ref'].split('/')[-1]
                repo_fullname = data['repository']['full_name']
                fork = data['repository']['fork']

                try:
                    branch_channels = self.phenny.config.branch_channels[repo_fullname][ref]
                except:
                    branch_channels = []

                for commit in data['commits']:
                    non_trunc = template.format(
                        data['repository']['name'], data['pusher']['name'],
                        ', '.join(commit['modified'] + commit['added']),
                        '{:}',
                        commit['url'][:commit['url'].rfind('/') + 7]
                    )

                    message = non_trunc.format(truncate(commit['message'], non_trunc.format('')))

                    if ref == 'master' and not fork:
                        msgs_default_channels.append(message)
                    else:
                        for channel in branch_channels:
                            if channel in msgs_by_channel:
                                msgs_by_channel[channel].append(message)
                            else:
                                msgs_by_channel[channel] = [message]
                        else:
                            silent_on_purpose = True

            elif event == 'release':
                template = '{:}: {:} * release {:} {:} {:}'
                tag = data['release']['tag_name']
                action = data['action']
                url = data['release']['html_url']
                msgs_default_channels.append(template.format(repo, user, tag, action, url))
            elif event == 'repository':
                template = 'new repository {:} {:} by {:} {:}'
                name = data['repository']['name']
                action = data['action']
                url = data['repository']['url']
                msgs_default_channels.append(template.format(name, action, user, url, url))
            elif event == 'team_add':
                template = 'repository {:} added to team {:} {:}'
                name = data['repository']['full_name']
                team = data['team']['name']
                msgs_default_channels.append(template.format(name, team))
            elif event == 'ping':
                template = 'ping from {:}, org: {:}'

                if 'organization' in data:
                    org = data['organization']
                else:
                    org = "no org specified!"

                sender = data['sender']['login']
                msgs_default_channels.append(template.format(sender, org))
            else:
                msgs_default_channels.append('sorry, event {:} not supported yet.'.format(event))
                msgs_default_channels.append(str(data.keys()))

        elif 'Jenkins' in self.headers['User-Agent']:
            msgs_default_channels.append('Jenkins: {}'.format(data['message']))
        # not github or Jenkins
        elif "commits" in data:
            for commit in data['commits']:
                try:
                    if "author" in commit:
                        # for bitbucket
                        message = self.return_data("bitbucket", data, commit)
                        msgs_default_channels.append(message)
                    else:
                        # we don't know which site
                        message = "unsupported data: " + str(commit)
                        msgs_default_channels.append(message)
                except Exception:
                    logger.warning("unsupported data: " + str(commit))

        if (not msgs_by_channel) and (not msgs_default_channels) and (not silent_on_purpose):
            # we couldn't get anything

            if event:
                msgs_default_channels.append("Don't know about '" + event + "' events")
            else:
                msgs_default_channels.append("Unable to deal with unknown event")

        # post all messages to all channels
        # except where specified in the config

        try:
            default_channels = self.phenny.config.git_channels[repo]
        except:
            default_channels = self.phenny.config.channels

        for message in msgs_default_channels:
            for channel in default_channels:
                if channel in msgs_by_channel:
                    msgs_by_channel[channel].append(message)
                else:
                    msgs_by_channel[channel] = [message]

        for channel in msgs_by_channel.keys():
            more.add_messages(self.phenny, channel, msgs_by_channel[channel])

        # send OK code
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def getBBFiles(self, filelist):
        '''Sort filelist into added, modified, and removed files
        (only for bitbucket).'''

        toReturn = {"added": [], "modified": [], "removed": []}
        for onefile in filelist:
            toReturn[onefile['type']].append(onefile['file'])
        return toReturn


def setup_server(phenny):
    '''Set up and start hooks server.'''

    global httpd

    if not httpd:
        httpd = PortReuseTCPServer(("", PORT), MyHandler(phenny))
        Thread(target=httpd.serve_forever).start()

    phenny.say("Server is up and running on port %s" % PORT)


def teardown(phenny):
    close_socket()
    phenny.say("Server has stopped on port %s" % PORT)


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
        phenny.say('{:s} {:s}'.format(truncate(msg, ' ' + url), url))
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
    phenny.say('{:s} {:s}'.format(truncate(msg, ' ' + url), url))
# command metadata and invocation
retrieve_commit.rule = ('$nick', 'info(?: +(.*))')
