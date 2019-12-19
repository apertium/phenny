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
* [flask](https://www.palletsprojects.com/p/flask/)
* [portalocker](https://github.com/WoLpH/portalocker)

## Installation
1. Run `./phenny` - this creates a default config file
2. Edit `~/.phenny/default.py`
3. Run `./phenny` - this now runs phenny with your settings

Enjoy!

## Testing
You will need the Python3 versions of `python-nose` and `python-mock`. To run
the tests, simply run `nosetests3`.

## Error reporting
phenny supports experimental error reporting to a Web app. You should not need
to configure phenny for this, as it is preconfigured. Just be sure that the
current directory is the top-level phenny directory (that contains this
README) when running phenny.

In the `error_server` directory, there are two scripts. `server.py` is a Web
app for accessing the logs. Edit it to set the variable `admin_password` to
the desired password. The username is `admin`. **Do not run this script
directly when in production!** Use a production WSGI server instead. To
access the logs, point your browser at its URL (the WSGI server should tell
you).

Also, be sure to periodically run `clean.py` in the same directory. This will
delete all logs over a week old. It is a good idea to make it a daily cron
job.

In case you cannot access the Flask app, or choose not to run it, you can run
`./extract.py <yyyy-mm-dd>` in the `error_server` directory to see logs from
that day.

Note that `server.py`, `extract.py`, and `clean.py` all require that their
current directory be `error_server`.

There is no way to "disable" error logging, but you do not have to run
server.py.

Also, please note that all times used for error logging are UTC.

## Authors
* Sean B. Palmer, http://inamidst.com/sbp/
* mutantmonkey, http://mutantmonkey.in
* Various [Apertium](https://apertium.org) developers
