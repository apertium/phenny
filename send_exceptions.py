#!/usr/bin/python3
import requests
import logging
from urllib.parse import quote_plus

logger = logging.getLogger('phenny')
class LogError(BaseException):
    pass

def log(text, url):
    logger.error(text)
    try:
        response = requests.get(url + '/report?error= ' + quote_plus(text))
        if response.status_code is not 200:
            raise LogError("logging server returned " + str(response.status_code))
    except:
        raise LogError("could not communicate with logging server")
