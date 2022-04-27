import json
import logging
import uuid
from functools import lru_cache
from typing import List, Optional, Union

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from models.film import FilmBrief
from models.person import Person
from services.rediscache import RedisCache, cache, cache_list
from services.service_utils import get_es_from_value

from fastapi.params import Depends

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.cache = RedisCache(redis)

    @cache(Person)
    async def get_person(self, person_id: uuid.UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index="persons", id=str(person_id))
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    @cache_list(Person)
    async def get_persons_search(self, search_query: str, size: int, page: int) -> Optional[List[Person]]:
        persons = await self._get_persons_es_search(search_query, page, size)
        if not persons:
            return None
        return persons

    @cache_list(FilmBrief)
    async def get_films_by_person(self, person_id: uuid.UUID, size: int, page: int) -> Optional[List[FilmBrief]]:
        films = await self._get_films_by_person_es(str(person_id), page, size)
        if not films:
            return None
        return films

    async def _get_films_by_person_es(self, person_id, page: int, size: int) -> Optional[List[FilmBrief]]:
        from_ = get_es_from_value(page, size)
        query = {
            "bool": {
                "should": [
                    {"nested": {"path": role, "query": {"term": {"{0}.uuid".format(role): person_id}}}}
                    for role in ["actors", "writers", "directors"]
                ]
            }
        }

        matched = await self.elastic.search(index="movies", query=query, from_=from_, size=size)
        if not matched:
            return None
        return [FilmBrief(**doc["_source"]) for doc in matched["hits"]["hits"]]

    async def _get_person_es(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index="persons", id=person_id)
        except NotFoundError:
            return None
        person = Person(**doc["_source"])
        return person

    async def _get_persons_es_search(self, search_query: str, page: int, size: int) -> Optional[List[Person]]:
        from_ = get_es_from_value(page, size)
        query = {"multi_match": {"query": search_query, "fields": ["full_name"]}}

        try:
            matched = await self.elastic.search(index="persons", query=query, size=size, from_=from_)
        except NotFoundError:
            return None
        return [Person(**doc["_source"]) for doc in matched["hits"]["hits"]]


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> PersonService:
    return PersonService(redis, elastic)
