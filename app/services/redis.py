import logging
import os
from typing import Optional, Union

import orjson
from aioredis import Redis
from services.base import BaseCacheStorage

log = logging.getLogger(os.path.basename(__file__))


class RedisStorage(BaseCacheStorage):
    def __init__(self, redis_client: Redis, expire: int = 60) -> None:
        self.redis = redis_client
        self.expire = expire

    async def get_from_storage(self, key) -> Optional[Union[list, dict]]:
        key_type = await self.redis.type(key)
        if key_type == b"none":
            return None
        if key_type == b"list":
            data_row = await self.redis.lrange(key, 0, -1)
            log.info("get_from_storage. return value is list. key: {0}".format(key))
            return [orjson.loads(row) for row in data_row[::-1]]
        if key_type == b"string":
            data_row = await self.redis.get(key)
            log.info("get_from_storage. return value is string. key: {0}".format(key))
            return orjson.loads(data_row)

    async def put_to_storage(self, key, payload) -> None:
        if not isinstance(payload, (dict, list)):
            raise ValueError("payload could be 'list' or 'str'")
        if isinstance(payload, list):
            # log.info("put_to_storage. payload: \n{0} ".format(payload))
            await self.redis.lpush(key, *list(map(lambda item: orjson.dumps(item), payload)))
            await self.redis.expire(key, self.expire)
        if isinstance(payload, dict):
            await self.redis.set(key, orjson.dumps(payload), ex=self.expire)
        log.info("put_to_storage. key: {0} ".format(key))
