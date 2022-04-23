from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from db.elastic import get_elastic
from db.redis import get_redis
from fastapi.params import Depends
from models.person import Person
from services.service_utils import get_es_from_value


class PersonService(object):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_persons_search(self, search_query: str, size: int, page: int) -> Optional[List[Person]]:
        return await self._get_person_es_search(search_query, page, size)

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
