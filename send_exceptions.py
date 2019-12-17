#!/usr/bin/python3
import requests
import logging
import datetime
import json
import portalocker
from urllib.parse import quote_plus

logger = logging.getLogger('phenny')
class LogError(BaseException):
    pass

def log(text, config):
    with portalocker.Lock(config.path_to_error_log) as _:
        logger.error(text)
        error = { 'timestamp': str(datetime.datetime.utcnow()), 'message': text}
        try:
            try:
                with open(config.path_to_error_log, 'r') as f:
                    logs = json.load(f)
            except Exception:
                logs = []

            with open(config.path_to_error_log, 'w+') as f:
                logs.append(error)
                json.dump(logs, f)

            return json.dumps(error)
        except Exception as e:
            logger.error('could not report to file')
            raise LogError from e
