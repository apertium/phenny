# phenny
[![Build Status](https://travis-ci.org/apertium/phenny.png?branch=master)](https://travis-ci.org/apertium/phenny)
[![Coverage Status](https://coveralls.io/repos/github/apertium/phenny/badge.svg?branch=master)](https://coveralls.io/github/apertium/phenny?branch=master)

This is phenny, a Python IRC bot. Originally written by Sean B. Palmer, it has
been ported to Python3.

This version comes with many new modules, IPv6 support, TLS support, and unit
tests.

Compatibility with existing phenny modules has been mostly retained, but they
will need to be updated to run on Python3 if they do not already. All of the
core modules have been ported, removed, or replaced.

## Requirements
* Python 3.4+
* [python-requests](http://docs.python-requests.org/en/latest/)
* [flask](https://www.palletsprojects.com/p/flask/) (see "Error reporting")

## Installation
1. Run `./phenny` - this creates a default config file
2. Edit `~/.phenny/default.py`
3. Run `./phenny` - this now runs phenny with your settings

Enjoy!

## Testing
You will need the Python3 versions of `python-nose` and `python-mock`. To run
the tests, simply run `nosetests3`.

## Error reporting
phenny supports error reporting through a specially designed Web app. This
uses a separate error reporting server. The error server is found in the
`error_scripts` directory as `server.py`. Edit this file to set the variable
`admin_password` to the desired password. The username is "admin". **Do not
run this script directly in production!** Use a production WSGI server
instead. Also, `clean.py` (in the same directory) should be run periodically
to delete old logs. Be sure to edit it so the `path_to_error_log` variable is
set to the actual path to the JSON file. This is `error_logs.json` in the
current directory used for `server.py`.

The error reporting URL is, by default, `http://localhost:8080`. If this is
not the host and port of the error reporting server, be sure to change it in
the main phenny configuration file; the variable is `error_host`. Set
`error_host` to `https://example.com` to disable error reporting.
(Technically, error reporting is still enabled, but example.com just "throws
away" any input.)

Visit the same URL of the error reporting server in a browser to see the
errors.

## Authors
* Sean B. Palmer, http://inamidst.com/sbp/
* mutantmonkey, http://mutantmonkey.in
* Various [Apertium](https://apertium.org) developers
