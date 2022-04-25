import logging
import uuid
from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import FilmBrief
from models.person import Person
from services.service_utils import get_es_from_value
from fastapi.params import Depends


class PersonService(object):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_person(self, person_id: uuid.UUID) -> Optional[Person]:
        return await self._get_person_es(str(person_id))

    async def get_persons_search(self, search_query: str, size: int, page: int) -> Optional[List[Person]]:
        return await self._get_person_es_search(search_query, page, size)

    async def get_film_by_person(self, person_id: uuid.UUID, size: int, page: int) -> Optional[List[FilmBrief]]:
        return await self._get_film_by_person_es(str(person_id), page, size)

    async def _get_film_by_person_es(self, person_id, page: int, size: int) -> Optional[List[FilmBrief]]:
        from_ = get_es_from_value(page, size)
        query = {
            "bool": {
                "should": [
                    {"nested": {"path": role, "query": {"term": {"{0}.uuid".format(role): person_id}}}}
                    for role in ["actors", "writers", "directors"]
                ]
            }
        }
        try:
            matched = await self.elastic.search(index="movies", query=query, from_=from_, size=size)
        except NotFoundError:
            return None
        return [FilmBrief(**doc["_source"]) for doc in matched["hits"]["hits"]]

    async def _get_person_es(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index="persons", id=person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def _get_person_es_search(self, search_query: str, page: int, size: int) -> Optional[List[Person]]:
        from_ = get_es_from_value(page, size)
        query = {"multi_match": {"query": search_query, "fields": ["full_name"]}}
        try:
            matched = await self.elastic.search(index="persons", query=query, size=size, from_=from_)
        except NotFoundError:
            return None
        return [Person(**doc["_source"]) for doc in matched["hits"]["hits"]]

    async def _get_person_cache(self):
        pass


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> PersonService:
    return PersonService(redis, elastic)
