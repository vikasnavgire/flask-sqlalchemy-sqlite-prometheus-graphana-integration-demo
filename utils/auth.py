from functools import wraps

from flask import request

from utils.constants import API_KEY
from utils.log import log


def authorization(func):
    @wraps(func)
    def check_authorization(*args, **kwargs):
        log.info("athorization ...")
        if request.headers.get("apiKey") == API_KEY:
            return func(*args, **kwargs)
        else:
            return "Unauthorised ", 403

    return check_authorization
