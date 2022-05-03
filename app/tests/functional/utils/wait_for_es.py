import logging
import os
import sys
import traceback

import requests
from backoff import backoff

from functional.config.settings import settings

log = logging.getLogger(os.path.basename(__file__))


@backoff(exception=Exception, retry=10, message={"error": "Ошибка подключения к ES."}, log=log)
def check(url):
    req = requests.get(url)
    status = req.status_code
    log.info(status)


if __name__ == "__main__":
    try:
        check(settings.es)
    except Exception:
        traceback.print_exc()
        log.error("Не удалось подключиться к ElasticSearch.")
        sys.exit(1)
