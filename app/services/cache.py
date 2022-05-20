import logging
import os

from db.redis import get_redis
from services.base import BaseCacheStorage
from services.redis import RedisStorage

log = logging.getLogger(os.path.basename(__file__))

TIME_OF_EXPIRE = 60 * 5  # in seconds


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


def cache(func):
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
