import json
import logging
from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from models.genre import Genre
from services.rediscache import RedisCache, cache_list

from fastapi.params import Depends


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.cache = RedisCache(redis)

    @cache_list(Genre)
    async def get_genres(self) -> Optional[List[Genre]]:
        query = {"match_all": {}}
        try:
            matched = await self.elastic.search(index="genres", query=query)
        except NotFoundError:
            return None
        return [Genre(**doc["_source"]) for doc in matched["hits"]["hits"]]


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> GenreService:
    return GenreService(redis, elastic)
