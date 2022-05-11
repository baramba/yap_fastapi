import logging
import os
import sys

import redis

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from config.settings import settings
from utils.backoff import backoff

log = logging.getLogger(os.path.basename(__file__))


@backoff(exception=redis.ConnectionError, retry=3, message={"error": "Ошибка подключения к Redis."}, log=log)
def check(host, port) -> None:
    r = redis.Redis(
        host=host,
        port=port,
        socket_connect_timeout=1,
        retry_on_timeout=False,
    )

    status = r.ping()
    log.info("Connect to Redis: {}".format(status))


if __name__ == "__main__":
    try:
        check(settings.redis_dsn.host, settings.redis_dsn.port)
    except redis.ConnectionError:
        log.error("Не удалось подключиться к Redis.")
        sys.exit(1)
