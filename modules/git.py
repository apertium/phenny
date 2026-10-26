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
from threading import Lock, Thread, Timer
import time
import urllib.parse

from modules import more
from tools import generate_report, PortReuseTCPServer, truncate
import web
from bot import event, command

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

    # Headers which are always present, per
    # https://docs.github.com/en/webhooks/webhook-events-and-payloads#delivery-headers
    expected_headers = [
        'X-GitHub-Hook-ID',
        'X-GitHub-Event',
        'X-GitHub-Delivery',
        'User-Agent',
        'X-GitHub-Hook-Installation-Target-Type',
        'X-GitHub-Hook-Installation-Target-ID',
    ]

    # Events which don't need to be reported to the chat
    ignored_events = {
        'branch_protection_configuration',
        'branch_protection_rule',
        'check_run',
        'check_suite',
        'code_scanning_alert',
        'custom_property',
        'custom_property_values',
        'dependabot_alert',
        'deploy_key',
        'deployment',
        'deployment_protection_rule',
        'deployment_review',
        'deployment_status',
        'fork',
        'github_app_authorization',
        'installation',
        'installation_repositories',
        'installation_target',
        'issue_dependencies',
        'issue_relates_to',
        'label',
        'marketplace_purchase',
        'member',
        'membership',
        'merge_group',
        'meta',
        'milestone',
        'org_block',
        'organization',
        'package',
        'page_build',
        'personal_access_token_request',
        'ping',
        'project',
        'project_card',
        'project_column',
        'projects_v2',
        'projects_v2_item',
        'projects_v2_status_update',
        'pull_request_review_thread',
        'registry_package',
        'repository_advisory',
        'repository_dispatch',
        'repository_ruleset',
        'repository_vulnerability_alert',
        'secret_scanning_alert',
        'secret_scanning_alert_location',
        'secret_scanning_scan',
        'security_advisory',
        'security_and_analysis',
        'sponsorship',
        'status',
        'sub_issues',
        'team',
        'team_add',
        'watch',
        'workflow_dispatch',
        'workflow_job',
    }

    message_templates = {
        'commit_comment': (
            '{repo}: {user} {action} comment on commit {commit}: {body}',
            {'commit': ['comment', 'commit_id'],
             'url': ['comment', 'html_url'],
             'body': ['comment', 'body']}),
        'create': (
            '{repo}: {user} created {ref_type} {ref}',
            {'ref': ['ref'], 'ref_type': ['ref_type']}),
        'delete': (
            '{repo}: {user} deleted {ref_type} {ref}',
            {'ref': ['ref'], 'ref_type': ['ref_type']}),
        'discussion': (
            '{repo}: {user} {action} discussion "{title}" {url}',
            {'title': ['discussion', 'title'],
             'url': ['discussion', 'html_url']}),
        'discussion_comment': (
            '{repo}: {user} {action} comment on discussion "{title}" {url}: {body}',
            {'title': ['discussion', 'title'],
             'url': ['discussion', 'html_url'],
             'body': ['comment', 'body']}),
        'gollum': (
            '{repo}: {user} {page_action} wiki page "{title}" {url}',
            {'page_action': ['pages', 'action'],
             'url': ['pages', 'html_url'],
             'title': ['pages', 'title']}),
        'issue_comment': (
            '{repo}: {user} {action} comment on {type} #{num} {url}: {body}',
            {'num': ['issue', 'number'],
             'url': ['issue', 'html_url'],
             'body': ['comment', 'body']}),
        'issues': (
            '{repo}: {user} {action} issue #{num}{rest} {url}',
            {'num': ['issue', 'number'],
             'url': ['issue', 'html_url']}),
        'public': ('{user} made the {repo} repository public', {}),
        'pull_request': (
            '{repo}: {user} {action} pull request #{num} "{title}" {url}',
            {'num': ['pull_request', 'number'],
             'title': ['pull_request', 'title'],
             'url': ['pull_request', 'html_url']}),
        'pull_request_review': (
            '{repo}: {user} {action} review on PR #{num} "{title}" {url}',
            {'num': ['pull_request', 'number'],
             'title': ['pull_request', 'title'],
             'url': ['pull_request', 'html_url']}),
        'pull_request_review_comment': (
            '{repo}: {user} {action} comment on PR #{num} "{title}" {url}',
            {'num': ['pull_request', 'number'],
             'title': ['pull_request', 'title'],
             'url': ['pull_request', 'html_url']}),
        'push': (
            '{repo}: {user} {action} commits [ {commits} ] {msgs}', {}),
        'release': (
            '{repo} release {release_tag} {action} by {user} {url}',
            {'release_tag': ['release', 'tag_name'],
             'url': ['release', 'html_url']}),
        'repository': (
            'repository {repo} {action} by {user} {repo_url}', {}),
        'repository_import': (
            '{user} imported repository {repo} {repo_url}', {}),
        'star': ('someone starred {repo}!', {}),
        'workflow_run': (
            '{repo}: workflow finished with status {status}: {url}',
            {'status': ['workflow_run', 'conclusion'],
             'url': ['workflow_run', 'html_url']}),
    }

    def validate_request_is_github(self):
        for header in self.expected_headers:
            if header not in self.headers:
                return False
        if not self.headers['User-Agent'].startswith('GitHub-Hookshot/'):
            return False
        return True

    # return error code because a GET request is meaningless
    def do_GET(self):
        self.send_response(405)
        self.end_headers()

    def do_POST(self):
        '''Handles POST requests for all hooks.'''
        receive_time = time.time()

        if not self.validate_request_is_github():
            logger.debug('Discarding non-Github payload; headers: '+str(self.headers))
            self.send_response(400)
            self.end_headers()
            return

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

            for admin in self.phenny.config.admins:
                self.phenny.msg(admin, 'Webhook received malformed payload')

            return

        status = 200 # OK
        channels, messages = [], []
        try:
            channels, messages = self.process_github_payload(data)
        except Exception as error:
            logger.error(str(error))
            status = 500 # Internal Server Error

        self.send_response(status)
        self.end_headers()
        self.finish()
        self.connection.close()

        send_time = time.time()
        respond_time = send_time - receive_time
        logger.debug("responded '{:}' in {:.2f}s".format(status, respond_time))

        # if anything went wrong, channels is an empty list, so this
        # does nothing
        for channel in channels:
            more.add_messages(self.phenny, channel, messages)

    def process_github_payload(self, data):
        config = self.phenny.config

        default_channels = config.git_channels.get('*', config.channels)
        channels = default_channels

        # both commit reports and error reports
        messages = []

        event = self.headers['X-GitHub-Event']
        if event in self.ignored_events:
            return [], []

        action = data.get('action', '')
        repo = data.get('repository', {}).get('full_name', '')

        in_config = False
        in_list = False
        if config.git_events:
            for key, value in config.git_events.items():
                if fnmatch(repo, key):
                    in_config = True
                    if event in value or (event + '_' + action) in value:
                        in_list = True
                        break
        if in_config and not in_list:
            return [], []
        if config.git_channels:
            for key, value in config.git_channels.items():
                if fnmatch(repo, key):
                    channels = value

        params = {
            'event': event,
            'action': action,
            'repo': repo,
            'user': data.get('sender', {}).get('login', 'someone'),
            'org': data.get('organization', {}).get('login', ''),
            'repo_url': data.get('repository', {}).get('url', ''),
        }

        def get_nested(dest, keys):
            nonlocal params, data
            obj = data
            for key in keys:
                obj = obj.get(key, {})
            params[dest] = obj or ''

        tmpl = 'Webhook notified of unknown event {event}'
        if event in self.message_templates:
            tmpl, args = self.message_templates[event]
            for dest, keys in args.items():
                get_nested(dest, keys)

            if event == 'commit_comment':
                params['commit'] = params['commit'][:7]
            elif event == 'issue_comment':
                params['type'] = 'issue'
                if 'pull_request' in data.get('issue', {}):
                    params['type'] = 'pull request'
                    if data['issue']['pull_request'].get('html_url'):
                        params['url'] = data['issue']['pull_request']['html_url']
            elif event == 'issues':
                params['rest'] = ''
                if 'assignee' in data:
                    params['rest'] = ' to '+data['assignee'].get('login', 'someone')
            elif event == 'pull_request_review_comment':
                blacklist = getattr(config, 'blacklist_pull_request_users', [])
                if params['user'] in blacklist:
                    return [], []
            elif event == 'push':
                if 'ref' in data and data['ref'].split('/')[-1] not in ['main', 'master']:
                    channels = getattr(config, 'branch_channels', {}).get(repo, {}).get(data['ref'], [])
                    if not channels:
                        return [], []
                params['action'] = 'pushed'
                if data.get('forced'):
                    params['action'] = 'force pushed'
                hashes = []
                msgs = []
                for com in data.get('commits', []):
                    hashes.append(com.get('id', '')[:7])
                    msgs.append(com.get('message', ''))
                params['commits'] = ', '.join(hashes)
                params['msgs'] = ' * '.join(msgs)
            elif event == 'star':
                if action != 'created':
                    return [], []
            elif event == 'workflow_run':
                if action != 'completed':
                    return [], []

        return channels, [truncate(tmpl.format_map(params))]

initial_setup_retry_time = 120 # 2 minutes
setup_retry_time = initial_setup_retry_time

def setup_server(phenny):
    '''Set up and start hooks server.'''

    global httpd, thread, setup_retry_time

    with lock:
        if httpd:
            return

        MyHandler.phenny = phenny
        try:
            httpd = PortReuseTCPServer(("", PORT), MyHandler)
            setup_retry_time = initial_setup_retry_time
        except OSError as e:
            logger.error("Could not start git hook server on port %s: %s", PORT, e)
            if setup_retry_time < (60 * 60): # 1 hour
                logger.error(f'Retrying in {setup_retry_time} seconds')
                t = Timer(setup_retry_time, setup_server, args=[phenny])
                t.start()
                setup_retry_time *= 2
            else:
                logger.error('Giving up on starting git hook server')
            return
        thread = Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()

@event('JOIN')
def auto_start(phenny, msg):
    if msg.nick != phenny.nick:
        return

    if phenny.config.githook_autostart:
        setup_server(phenny)

@command('manualstart')
def manual_start(phenny, input):
    phenny.reply("gonna try to setup_server and see if it crashes")
    teardown(phenny)
    setup_server(phenny)

def teardown(phenny):
    phenny.say("TEARING DOWN SERVER!")
    if lock.locked():
        lock.release()
    if thread is not None:
        thread.join(timeout=0)
    close_socket()

@command('gitserver')
def gitserver(phenny, msg):
    '''Control git server. Possible commands are:
        .gitserver status (all users)
        .gitserver start (admins only)
        .gitserver stop (admins only)'''

    global httpd

    command = msg.command_args
    if phenny.is_admin(msg.nick):
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

@command('to_commit')
def to_commit(phenny, msg):
    api = "https://api.github.com/search/commits?q=%s"
    # currently experimental API
    headers = { "Accept": "application/vnd.github.cloak-preview" }

    sha = msg.command_args
    commit_json = web.get(api % sha, headers=headers)
    data = json.loads(commit_json)

    item = data["items"][0]
    html_url = item["html_url"]

    phenny.reply(html_url)

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

@command('recent_commits', thread=True)
def get_recent_commit(phenny, msg):
    '''Get recent commit information for each repository Begiak monitors.'''

    for repo in phenny.config.git_repositories:
        html = web.get(phenny.config.git_repositories[repo] + '/commits')
        data = json.loads(html)
        # the * is for unpacking
        info, url = get_commit_info(phenny, repo, data[0]['sha'])
        msg = generate_report(repo, *info)
        # the URL is truncated so that it has at least 6 sha characters
        url = url[:url.rfind('/') + 7]
        phenny.say(truncate(msg, '{} ' + url))

@command('commit_info')
def retrieve_commit(phenny, msg):
    '''Retreive commit information for a given repository and revision. This
    command is called as 'begiak: info <repo> <rev>'.'''

    if len(msg.command_args_list) != 2:
        phenny.reply("Invalid number of parameters.")
        return

    repo = msg.command_args_list[0]
    rev = msg.command_args_list[1]

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
