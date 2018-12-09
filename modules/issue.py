"""
issue.py - create a new GitHub issue
author: amuritna
"""
from web import is_up, post
from requests import HTTPError
import json

gh_uri = 'https://api.github.com'
allowed_owners = ['apertium'] # makes checking for valid owner/repo combo faster
default_desc = 'This issue was automatically made by begiak, Apertium\'s beloved IRC bot, by the order of {} on #apertium. A human is yet to update the description.'
invalidmsg = 'Invalid .issue command. Usage: .issue <owner>/<repository> <title>'

def issue(phenny, input):
    """ .issue <owner>/<repository> <title> - create a new GitHub issue """    
 
    if not is_up(gh_uri):
        return phenny.reply('Sorry, GitHub is down.')
	
    # check if GitHub auth token is available in default.py
    try:
        oauth_token = phenny.config.gh_oauth_token
    except AttributeError:
        return phenny.reply('GitHub authentication token needs to first be set in the configuration file (default.py)')
		
    # check input validity
    if not input.group(1):
        return phenny.reply(invalidmsg)

    content = ''.join(input.group(1)).strip()
    ghpath = content.split()[0].split('/')
        
    # check whether likely in an owner/repository combo format
    if len(ghpath) != 2:
        return phenny.reply(invalidmsg)

    owner = ghpath[0]
    repo = ghpath[1]

    if owner not in allowed_owners:
        return phenny.reply('Begiak cannot create an issue there.')

    title = ' '.join(content.split()[1:]).strip()
    if len(title) < 1:
        return phenny.reply(invalidmsg)

    # build and post HTTP request
    req_url = '{}/repos/{}/{}/issues'.format(gh_uri, owner, repo)
    req_headers = {'Authorization': 'token {}'.format(oauth_token)}
    req_body = json.dumps({
        "title": title,
        "body": default_desc.format(input.nick)
    })

    try:
        req_str = post(req_url, req_body, req_headers)
        req_json = json.loads(req_str)
        phenny.reply('Issue created. You can add a description at {}'.format(req_json['html_url']))
    except HTTPError:
        phenny.reply('It appears that the repository you provided does not exist.')

issue.commands = ['issue']
issue.priority = 'medium'
issue.example = '.issue apertium/phenny Commit messages with multiple authors showing the less relevant one'

if __name__ == "__main__":
    print(__doc__.strip())
