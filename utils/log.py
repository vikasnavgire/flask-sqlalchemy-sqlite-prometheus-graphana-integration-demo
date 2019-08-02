# applications logger

import logging

log = logging.getLogger("app_log")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG
            )
formatter = logging.Formatter("|%(asctime)s |%(levelname)s | %(filename)s | %(module)s| %(lineno)d | %(message)s")

ch.setFormatter(formatter)
log.addHandler(ch)
