import uuid
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from services.cache import cache2
from services.service_utils import get_es_from_value

from fastapi.params import Depends

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @cache2
    async def get_person(self, person_id: uuid.UUID) -> Optional[dict]:
        try:
            doc = await self.elastic.get(index="persons", id=str(person_id))
        except NotFoundError:
            return None
        return doc["_source"]

    @cache2
    async def get_persons_search(self, search_query: str, size: int, page: int) -> Optional[list[dict]]:

        from_ = get_es_from_value(page, size)
        query = {"multi_match": {"query": search_query, "fields": ["full_name"]}}

        try:
            matched = await self.elastic.search(index="persons", query=query, size=size, from_=from_)
        except NotFoundError:
            return None
        return [doc["_source"] for doc in matched["hits"]["hits"]]

    @cache2
    async def get_films_by_person(self, person_id: uuid.UUID, size: int, page: int) -> Optional[list[dict]]:
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

        return [doc["_source"] for doc in matched["hits"]["hits"]]


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> PersonService:
    return PersonService(redis, elastic)
