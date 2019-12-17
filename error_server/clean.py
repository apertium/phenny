#!/usr/bin/env python3
import json
import portalocker
from datetime import datetime

path_to_error_log = 'error_logs.json'
with portalocker.Lock(path_to_error_log) as _:
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
