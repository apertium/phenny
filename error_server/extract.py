#!/usr/bin/env python3
import json
import sys
import datetime

def valid_date(datestring):
    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False

if len(sys.argv) is not 2 or not valid_date(sys.argv[1]):
    print('usage: ' + sys.argv[0] + ' <yyyy-mm-dd>')
    exit(1)

try:
    with open('error_logs.json', 'r') as f:
        all_logs = json.load(f)
        logs = [log for log in all_logs if (log['timestamp'][:10].strip() == sys.argv[1].strip())]

        for log in logs:
            print('LOG FROM ' + log['timestamp'] + ':')
            print(log['message'])
            print('----------------------------------------')

        if len(logs) is 0:
            print('No logs.')
except:
    print('an error occurred. are you in the error_server directory, and does the error_logs.json file exist?')
