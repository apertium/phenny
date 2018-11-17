"""
issue.py - create a new GitHub issue
author: amuritna
"""
# TODO: add tests
# TODO: use web module
import requests
import json

# TODO: use phenny config
oauth_token = 'PUT OAUTH TOKEN HERE'

gh_uri = 'https://api.github.com'
allowed_owners = ['apertium'] # makes checking for valid owner/repo combo faster
default_desc = 'This issue was automatically made by begiak, Apertium\'s beloved IRC bot, by the order of someone on #apertium. A human is yet to update the description.'

invalidmsg = 'Invalid .issue command. Usage: .issue <owner>/<repository> <title>'

def issue(phenny, input):
	""" .issue <owner>/<repository> <title> - create a new GitHub issue """    
 
	gh_check = requests.head(gh_uri)
	if gh_check.status_code != 200:
		return phenny.reply('Sorry, GitHub is down.')

    # check input validity
	try:
		if not input.group(1):
			return phenny.reply(invalidmsg)

		content = input.group(1).strip()
		ghpath = content.split()[0].split('/')
        
		# check whether likely in an owner/repository combo format
		if len(ghpath) != 2:
			return phenny.reply(invalidmsg)

		owner = ghpath[0]
		repo = ghpath[1]

		if owner not in allowed_owners:
			return phenny.reply('Begiak cannot create an issue there.')

		title = " ".join(content.split()[1:]).strip()
		if len(title) < 1:
			return phenny.reply(invalidmsg)

	except SyntaxError:
		return phenny.reply(invalidmsg)

	# build and post HTTP request
	req_target = gh_uri + '/repos/' + owner + '/' + repo + '/issues'
	req_params = {'access_token': oauth_token}
	req_body = json.dumps({
		"title": title,
		"body": default_desc
	})

	req_issue = requests.post(req_target, params=req_params, data=req_body)

	# return final feedback - successfully created issue? repo not found?
	if req_issue.status_code == 404:
		return phenny.reply('It looks like that repository doesn\'t exist...')

	return phenny.reply('Issue created. You can add a description at ' + req_issue.json()["html_url"])


issue.commands = ['issue']
issue.priority = 'medium'
issue.example = '.issue apertium/phenny Commit messages with multiple authors showing the less relevant one'

if __name__ == "__main__":
	print(__doc__.strip())

