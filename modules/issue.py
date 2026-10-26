"""
issue.py - create a new GitHub issue
author: amuritna
"""
import web
from requests import HTTPError
import json
from bot import command

gh_uri = 'https://api.github.com'
default_desc = 'This issue was automatically made by begiak, Apertium\'s beloved IRC bot, by the order of {} on #apertium. A human still needs to update the description.'
invalidmsg = 'Invalid .issue command. Usage: .issue <owner>/<repository> <title>'

@command('issue', example='.issue apertium/phenny Commit messages with multiple authors showing the less relevant one')
def issue(phenny, msg):
    """ .issue <owner>/<repository> <title> - create a new GitHub issue """

    if not web.is_up(gh_uri):
        return phenny.reply('Sorry, GitHub is down.')

    # check if GitHub auth token is available in default.py
    try:
        oauth_token = phenny.config.gh_oauth_token
    except AttributeError:
        return phenny.reply('GitHub authentication token needs to first be set in the configuration file (default.py)')

    # check input validity
    if not msg.command_args:
        return phenny.reply(invalidmsg)

    dest = msg.command_args_list[0]
    if dest.startswith('-'):
        dest = 'apertium' + dest
    if '/' not in dest:
        dest = 'apertium/' + dest
    ghpath = dest.split('/')

    # check whether likely in an owner/repository combo format
    if len(ghpath) != 2:
        return phenny.reply(invalidmsg)

    owner = ghpath[0]
    repo = ghpath[1]

    allowed_owners = getattr(phenny.config, 'git_issue_allowed_owners',
                             ['apertium'])
    if owner not in allowed_owners:
        return phenny.reply('Begiak cannot create an issue there.')

    title = ' '.join(msg.command_args_list[1:])
    if len(title) < 1:
        return phenny.reply(invalidmsg)

    # build and post HTTP request
    req_url = '{}/repos/{}/{}/issues'.format(gh_uri, owner, repo)
    req_headers = {'Authorization': 'token {}'.format(oauth_token)}
    req_body = json.dumps({
        "title": title,
        "body": default_desc.format(msg.nick)
    })

    try:
        req_str = web.post(req_url, req_body, req_headers)
        req_json = json.loads(req_str)
        phenny.reply('Issue created. You should add a description at {}'.format(req_json['html_url']))
    except HTTPError as e:
        print(e)
        phenny.reply('It appears that the repository you provided does not exist.')

if __name__ == "__main__":
    print(__doc__.strip())
