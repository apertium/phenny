#!/usr/bin/env python3
from datetime import datetime
import json

path_to_error_log = '/home/scoopgracie/projects/phenny/error_logs.json'
with open(path_to_error_log, 'r') as f:
    data = json.load(f)

def date_diff():
    date = datetime.strptime(data[0]['timestamp'].split(' ')[0], "%Y-%m-%d")
    now = datetime.utcnow()
    diff = now - date
    return(diff)

try:
    while date_diff().days > 7:
        data.pop(0)
except Exception:
    pass

with open(path_to_error_log, 'w+') as f:
    json.dump(data, f)
