#!/usr/bin/env python3
#https://creativecommons.org/licenses/by-sa/4.0/
admin_password = 'password'

from flask import Flask, abort, request, Response
from urllib.parse import quote_plus
from functools import wraps
import datetime
import json


app = Flask(__name__)

#begin section adapted from https://stackoverflow.com/a/29725558 by user "dirn", used under https://creativecommons.org/licenses/by-sa/4.0/.
def check_auth(username, password):
    return username == 'admin' and password == admin_password

def authenticate():
    return Response(
    '<h1>401 Login Required</h1><p>This endpoint requires a login.</p>\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
#end section

def template(title, content, is_home):
    return('''<!DOCTYPE html>
<html lang=en>
    <head>
        <title>''' + ( ( title + ' - ' ) if title else '' ) + '''begiak Error Log</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <header>
            <h1>begiak Error Log</h1>
            <nav>''' + ( '<b>Log Home</b>' if is_home else '<a href=/>Log Home</a>' ) + ''' - <a href=http://wiki.apertium.org/wiki/Begiak>begiak (Apertium Wiki)</a> - <a href=https://github.com/apertium/phenny>Begiak on GitHub</a> - <a href=https://apertium.org>Apertium</a></nav>
            <aside>If you aren't debugging Begiak, this probably isn't what you're looking for. Try one of the other links above.</aside>
        </header>
        <main>''' + content + '''</main>
        <footer>Made by <a href=https://scoopgracie.com>ScoopGracie</a> for <a href=https://apertium.org>Apertium</a></footer>
    </body>
</html>''')
    
@app.route('/')
@requires_auth
def root():
    try:
        with open('error_logs.json', 'r') as f:
            logs = json.load(f)
    except Exception:
        logs = []

    if len(logs) == 0:
        links = '<p>No records.</p>'
    else:
        logs.reverse()

        links = '<ul>'

        for log in logs:
            links += '<li><a href="/view?log=' + quote_plus(log['timestamp']) + '">' + log['timestamp'] + '</a></li>'

        links += '</ul>'

    return template(None, links, True)

@app.route('/view')
@requires_auth
def view():
    try:
        with open('error_logs.json', 'r') as f:
            logs = json.load(f)
    except Exception:
        logs = []

    content = None

    for log in logs:
        content = None

        if log['timestamp'] == request.args.get('log'):
            title = log['timestamp']
            content = '<h2>Log for ' + log['timestamp'] + '</h2><textarea style="width: 95vw; height: 50vh">' + log['message'] + '</textarea>'
            break

    if content is None:
        abort(500)

    return template(title, content, False)

@app.route('/report')
def report():
    error = { 'timestamp': str(datetime.datetime.utcnow()), 'message': request.args.get('error') }
    try:
        try:
            with open('error_logs.json', 'r') as f:
                logs = json.load(f)
        except Exception:
            logs = []

        with open('error_logs.json', 'w+') as f:
            logs.append(error)
            json.dump(logs, f)

        return json.dumps(error)
    except Exception as e:
        abort(500)
        raise e

@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Disallow: /'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
