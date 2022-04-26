import json
import logging
import uuid
from functools import lru_cache
from http import HTTPStatus
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from models.film import Film
from services.rediscache import RedisCache, cache, cache_list
from services.service_utils import get_es_from_value

from fastapi.exceptions import HTTPException
from fastapi.params import Depends

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.cache = RedisCache(redis)

    @cache(Film)
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    @cache_list(Film)
    async def get_films(
        self,
        sort: str,
        size: int = 1,
        page: int = 0,
        genre: Optional[uuid.UUID] = None,
    ) -> Optional[List[Film]]:

        query = {"match_all": {}}

        if genre:
            query = {"nested": {"path": "genre", "query": {"term": {"genre.uuid": genre}}}}

        films = []
        from_ = get_es_from_value(page, size)

        try:
            matched_docs = await self.elastic.search(index="movies", query=query, sort=sort, size=size, from_=from_)
        except NotFoundError:
            return None

        for doc in matched_docs["hits"]["hits"]:
            films.append(Film(**doc["_source"]))

        return films

    @cache_list(Film)
    async def get_films_search(
        self,
        search_query: str,
        page: int = 0,
        size: int = 1,
    ) -> Optional[List[Film]]:
        query = {"multi_match": {"query": search_query, "fields": ["title", "description"]}}

        films = []
        from_ = get_es_from_value(page, size)
        try:
            matched_docs = await self.elastic.search(index="movies", query=query, size=size, from_=from_)
        except NotFoundError:
            return None
        for doc in matched_docs["hits"]["hits"]:
            films.append(Film(**doc["_source"]))
        return films


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> FilmService:
    return FilmService(redis, elastic)
