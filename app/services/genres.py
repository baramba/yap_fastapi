import json
import logging
from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from db.elastic import get_elastic
from db.redis import get_redis
from fastapi.params import Depends
from models.genre import Genre


class GenreService(object):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_genres(self) -> Optional[List[Genre]]:
        return await self._get_genres_es()

    async def _get_genres_es(self) -> Optional[List[Genre]]:
        query = {"match_all": {}}

        cache_key = '-'.join(['genres', json.dumps(query)])
        genres = self._list_genre_cache(cache_key)
        if not genres:
            try:
                matched = await self.elastic.search(index="genres", query=query)
            except NotFoundError:
                return None
            genres = [Genre(**doc["_source"]) for doc in matched["hits"]["hits"]]
            await self._put_list_genres_cache(cache_key, genres)

        return genres

    async def _list_genre_cache(self, list_name: str) -> Optional[List[Genre]]:
        genres_row = await self.redis.lrange(str(list_name), 0, -1)
        if not genres_row:
            return None

        logging.info('Get list from cache')
        return [Genre.parse_raw(genre_row) for genre_row in genres_row]

    async def _put_list_genres_cache(self, list_name: str, genres: List[Genre]) -> None:
        logging.info('Save genres list to cache')
        await self.redis.lpush(list_name, *[genre.json() for genre in genres])


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> GenreService:
    return GenreService(redis, elastic)
