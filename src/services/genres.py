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
        try:
            matched = await self.elastic.search(index="genres", query=query)
        except NotFoundError:
            return None

        return [Genre(**doc["_source"]) for doc in matched["hits"]["hits"]]

    async def _get_genre_cache(self):
        pass


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> GenreService:
    return GenreService(redis, elastic)
