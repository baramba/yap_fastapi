import abc
import logging
import os
from typing import Optional, Union

import orjson
from aioredis import Redis
from db.redis import get_redis

log = logging.getLogger(os.path.basename(__file__))

TIME_OF_EXPIRE = 60 * 5  # in seconds


class BaseCacheStorage:

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    async def get_from_storage(self, key: str) -> Union[list, str]:
        """Прочитать данные из хранилища кэша"""

    @abc.abstractmethod
    async def put_to_storage(self, key: str, value: Union[list, str]) -> None:
        """Сохранить данные в хранилище кэша"""


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


class Cache:
    cache_storage: BaseCacheStorage

    def __init__(self, cache_storage: BaseCacheStorage) -> None:
        Cache.cache_storage = cache_storage

    @staticmethod
    def get_key(name: str, params: tuple) -> str:
        key = "-".join([str(param) for param in params])
        key = "-".join((key, name))
        return key

    async def get_from_cache(self, key):
        values = await Cache.cache_storage.get_from_storage(key)
        return values

    async def put_to_cache(self, key, value):
        await self.cache_storage.put_to_storage(key, value)


async def get_cache() -> Cache:
    cache = Cache(
        RedisStorage(
            await get_redis(),
            expire=TIME_OF_EXPIRE,
        )
    )
    log.info("Retrun cahce object:{0}".format(cache))
    return cache


def cache2(func):
    async def wrapper(self, *args, **kwargs):
        cache = await get_cache()
        params = [*args, *kwargs.keys(), *kwargs.values()]
        cache_key = cache.get_key(func.__name__, params)
        data_row = await cache.get_from_cache(cache_key)
        if not data_row:
            result = await func(self, *args, **kwargs)
            if result:
                await cache.put_to_cache(cache_key, result)
            return result
        return data_row

    return wrapper
