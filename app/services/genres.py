import uuid
from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from models.genre import Genre
from services.rediscache import RedisCache, cache, cache_list
from services.service_utils import get_es_from_value

from fastapi.params import Depends


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.cache = RedisCache(redis)

    @cache_list(Genre)
    async def get_genres(self, size: int, page: int) -> Optional[List[Genre]]:
        query = {"match_all": {}}
        from_ = get_es_from_value(page, size)
        try:
            matched = await self.elastic.search(index="genres", query=query, size=size, from_=from_)
        except NotFoundError:
            return None
        return [Genre(**doc["_source"]) for doc in matched["hits"]["hits"]]

    @cache_list(Genre)
    async def get_genres_search(self, search_query: str, size: int, page: int) -> Optional[List[Genre]]:
        query = {"match": {"name": {"query": search_query, "fuzziness": "AUTO"}}}
        from_ = get_es_from_value(page, size)
        try:
            matched = await self.elastic.search(index="genres", query=query, size=size, from_=from_)
        except NotFoundError:
            return None
        return [Genre(**doc["_source"]) for doc in matched["hits"]["hits"]]

    @cache(Genre)
    async def get_genre(self, genre_id: uuid.UUID) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index="genres", id=str(genre_id))
        except NotFoundError:
            return None
        return Genre(**doc["_source"])


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> GenreService:
    return GenreService(redis, elastic)
