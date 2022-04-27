import hashlib
import logging
from curses import wrapper
from typing import List, Optional

from aioredis import Redis
from models.basemodel import BaseApiModel

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class RedisCache:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def get_key(self, name: str, params: tuple) -> str:
        key = "-".join([str(param) for param in params])
        key = "-".join((key, name))
        return key

    async def get_row(self, key: str) -> Optional[str]:
        data_row = await self.redis.get(key)

        if not data_row:
            return None
        logging.info("Get {0} from cache".format(key))
        return data_row

    async def put_row(self, key: str, payload: str) -> None:
        logging.info("Save {0} to cache".format(key))
        await self.redis.set(key, payload, ex=CACHE_EXPIRE_IN_SECONDS)

    async def get_rows(self, key: str) -> Optional[list]:
        data_row = await self.redis.lrange(key, 0, -1)
        if not data_row:
            return None
        logging.info("Get {0} from cache".format(key))
        return data_row[::-1]

    async def put_rows(self, key: str, payload: list) -> None:
        logging.info("Save {0} to cache".format(key))
        await self.redis.lpush(key, *payload)
        await self.redis.expire(key, CACHE_EXPIRE_IN_SECONDS)


def cache(cached_obj: BaseApiModel):
    def wrapp(func):
        async def inner(self, *args, **kwargs) -> BaseApiModel:
            cache = RedisCache(self.redis)
            cache_key = cache.get_key(func.__name__, args)
            data_row = await cache.get_row(cache_key)
            if not data_row:
                result = await func(self, *args, *kwargs)
                if result:
                    await cache.put_row(cache_key, result.json())
                return result
            return cached_obj.parse_raw(data_row)

        return inner

    return wrapp


def cache_list(cached_obj: BaseApiModel):
    def wrapp(func):
        async def inner(self, *args, **kwargs) -> List[BaseApiModel]:
            cache = RedisCache(self.redis)
            cache_key = cache.get_key(func.__name__, args)
            data_rows = await cache.get_rows(cache_key)

            if not data_rows:
                result = await func(self, *args, *kwargs)
                if result:
                    await self.cache.put_rows(cache_key, [result.json() for result in result])
                return result
            return [cached_obj.parse_raw(row) for row in data_rows]

        return inner

    return wrapp
