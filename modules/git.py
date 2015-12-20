#!/usr/bin/env python
"""
git.py - Github Post-Receive Hooks Module
"""

import http.server
from io import StringIO
import json
import os
import re
import socketserver
import time
from tools import generate_report
import urllib.parse
import web

# githooks port
PORT = 1234

# module-global variables
Handler = None
httpd = None


# githooks handler
class MyHandler(http.server.SimpleHTTPRequestHandler):
    phenny = None
    phInput = None

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
        self.send_response(403)

    def do_POST(self):
        '''Handles POST requests for all hooks.'''

        # read and decode data
        length = int(self.headers['Content-Length'])
        indata = self.rfile.read(length)
        post_data = urllib.parse.parse_qs(indata.decode('utf-8'))
        if len(post_data) == 0:
            post_data = indata.decode('utf-8')
        if "payload" in post_data:
            data = json.loads(post_data['payload'][0])
        else:
            data = json.loads(post_data)

        # msgs will contain both commit reports and error reports
        msgs = []
        
        # handle GitHub triggers
        if 'GitHub' in self.headers['User-Agent']:
            event = self.headers['X-Github-Event']
            user = data['sender']['login']
            repo = data['repository']['name']            
            if event == 'commit_comment':
                commit = data['comment']['commit_id'][:7]
                comment = data['comment']['body']
                url = data['comment']['html_url']
                url = url[:url.rfind('/') + 7]
                msgs.append('{:}: {:} * new comment on commit {:}: {:} {:}' \
                            .format(repo, user, commit, comment, url))
            elif event == 'create' or event == 'delete':
                ref = data['ref']
                type_ = data['ref_type']
                msgs.append('{:}: {:} * {:} {:} {:}d {:}' \
                            .format(repo, user, type_, ref, event))
            elif event == 'fork':
                url = data['forkee']['html_url']
                msgs.append('{:}: {:} forked this repo {:}' \
                            .format(repo, user, url))
            elif event == 'issue_comment':
                number = data['issue']['number']
                comment = data['comment']['body']
                url = data['issue']['html_url']
                msgs.append('{:}: {:} * new comment on issue #{:}: {:} {:}' \
                            .format(repo, user, number, comment, url))
            elif event == 'issues':
                number = data['issue']['number']
                title = data['issue']['title']
                action = data['action']
                url = data['issue']['html_url']
                opt = ''
                if data['issue']['assignee'] is not None:
                    opt = 'to ' + data['issue']['assignee']
                elif 'label' in data:
                    opt = 'with ' + data['label']['name']
                msgs.append('{:}: {:} * issue #{:} "{:}" {:} {:} {:}' \
                            .format(repo, user, number, title, action, opt, url))
            elif event == 'member':
                new_user = data['member']['login']
                action = data['action']
                msgs.append('{:}: {:} * user {:} {:} as collaborator {:}' \
                            .format(repo, user, new_user, action))
            elif event == 'membership':
                new_user = data['member']['login']
                action = data['action']
                prep = ['to', 'from'][int(action == 'removed')]
                scope = data['scope']
                name = data['team']['name']
                msgs.append('{:}: user {:} {:} {:} {:} {:} {:}' \
                            .format(repo, new_user, action, prep, scope, name))
            elif event == 'pull_request':
                number = data['number']
                title = data['pull_request']['title']
                action = data['action']
                url = data['pull_request']['html_url']
                opt = ''
                if data['pull_request']['assignee'] is not None:
                    opt = 'to ' + data['pull_request']['assignee']
                msgs.append('{:}: {:} * pull request #{:} "{:}" {:} {:} {:}' \
                            .format(repo, user, number, title, action, opt, url))
            elif event == 'pull_request_review_comment':
                number = data['pull_request']['number']
                comment = data['comment']['body']
                url = data['comment']['html_url']
                msgs.append('{:}: {:} * new comment on pull request #{:}: {:} {:}' \
                            .format(repo, user, number, comment, url))
            elif event == 'push':
                for commit in data['commits']:
                    msgs.append(self.return_data("github", data, commit) \
                            + ' ' + commit['url'][:commit['url'].rfind('/') + 7])
            elif event == 'release':
                tag = data['release']['tag_name']
                action = data['action']
                url = data['release']['html_url']
                msgs.append('{:}: {:} * release {:} {:} {:}' \
                            .format(repo, user, tag, action, url))
            elif event == 'repository':
                name = data['repository']['name']
                action = data['action']
                url = data['repository']['url']
                msgs.append('new repository {:} {:} by {:} {:}' \
                            .format(name, action, user, url, url))
            elif event == 'team_add':
                name = data['repository']['full_name']
                team = data['team']['name']
                msgs.append('repository {:} added to team {:} {:}' \
                            .format(name, team))
            else:
                msgs.append('sorry, event {:} not supported yet.'.format(event))
                msgs.append(data.keys())
        # not github
        elif "commits" in data:
            for commit in data['commits']:
                try:
                    if "author" in commit:
                        # for bitbucket
                        msgs.append(self.return_data("bitbucket", data,
                                                     commit))
                    else:
                        # we don't know which site
                        msgs.append("unsupported data: " + str(commit))
                except Exception:
                    print("unsupported data: " + str(commit))
        elif "project_name" in data:
            # for googlecode
            # still experimental, so notify firespeaker and write debug log
            self.phenny.bot.msg("firespeaker", "DEBUG" + repr(data))
            with open("/home/begiak/DEBUG.txt", "a") as debugf:
                debugf.write(repr(data) + "\n\n")

            for commit in data['revisions']:
                msgs.append(self.return_data("googlecode", data, commit))

        if (not msgs) and (data['commits']):
            # we couldn't get anything
            # sometimes github sends empty pushes (eg. for releases), so check
            # the data
            msgs = ["Something went wrong: " + str(data.keys())]

        # post all messages to all channels
        for msg in msgs:
            for chan in self.phInput.chans:
                if msg != None:
                    self.phenny.bot.msg(chan, msg)

        # send OK code and notify firespeaker
        self.send_response(200)
        # self.phenny.bot.msg("firespeaker", "200 OK")

    def getBBFiles(self, filelist):
        '''Sort filelist into added, modified, and removed files
        (only for bitbucket).'''

        toReturn = {"added": [], "modified": [], "removed": []}
        for onefile in filelist:
            toReturn[onefile['type']].append(onefile['file'])
        return toReturn


def setup_server(phenny, input):
    '''Set up and start hooks server.'''

    global Handler, httpd
    Handler = MyHandler
    Handler.phenny = phenny
    Handler.phInput = input
    httpd = socketserver.TCPServer(("", PORT), Handler)
    phenny.say("Server is up and running on port %s" % PORT)
    httpd.serve_forever()


def github(phenny, input):
    '''Set up and start server automatically on successfully connecting to an
    IRC network (called automatically).'''

    global Handler, httpd
    if Handler is None and httpd is None:
        if httpd is not None:
            httpd.shutdown()
            httpd = None
        if Handler is not None:
            Handler = None
        setup_server(phenny, input)
# command metadata and invocation event
github.name = 'start githook server'
github.event = "PONG"
github.rule = r'.*'
github.priority = 'medium'


def stopserver(phenny, input):
    '''Stop hooks server. This command, 'stopserver', is the same as
    '.gitserver stop' and can only be run by an admin.'''

    global Handler, httpd
    if input.admin:
        # we're admin
        if httpd is not None:
            httpd.shutdown()
            httpd = None
        Handler = None
        phenny.say("Server has stopped on port %s" % PORT)
    else:
        phenny.reply("That is an admin-only command.")
# command invocation
stopserver.commands = ['stopserver']


def gitserver(phenny, input):
    '''Control git server. Possible commands are:
        .gitserver status (all users)
        .gitserver start (admins only)
        .gitserver stop (admins only)'''

    global Handler, httpd

    command = input.group(1).strip()
    if input.admin:
        # we're admin
        # everwhere below, 'httpd' being None indicates that the server is not
        # running at the moment
        if command == "stop":
            if httpd is not None:
                stopserver(phenny, input)
            else:
                phenny.reply("Server is already down!")
        elif command == "start":
            if httpd is None:
                setup_server(phenny, input)
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

    return (author, comment, modified_paths, added_paths, removed_paths, rev,\
        date), url


def get_recent_commit(phenny, input):
    '''Get recent commit information for each repository Begiak monitors. This
    command is called as 'begiak: recent'.'''

    for repo in phenny.config.git_repositories:
        html = web.get(phenny.config.git_repositories[repo] + '/commits')
        data = json.loads(html)
        # the * is for unpacking
        info, url = get_commit_info(phenny, repo, data[0]['sha'])
        msg = generate_report(repo, *info)
        # the URL is truncated so that it fits
        phenny.say(msg + ' ' + url[:60])
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
    phenny.say(msg + ' ' + url[:60])
retrieve_commit.rule = ('$nick', 'info(?: +(.*))')
