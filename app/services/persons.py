import json
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

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


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

        cache_key = '-'.join(['persons', json.dumps(query), str(page), str(size)])
        
        result = self._get_list_persons_cache(cache_key)
        if not result:
            try:
                matched = await self.elastic.search(index="movies", query=query, from_=from_, size=size)
            except NotFoundError:
                return None
            result = [FilmBrief(**doc["_source"]) for doc in matched["hits"]["hits"]]
            await self._put_list_films_cache(cache_key, result)
        return result

    async def _get_person_es(self, person_id: str) -> Optional[Person]:
        person = await self._get_person_cache(person_id)
        if not person:
            try:
                doc = await self.elastic.get(index="persons", id=person_id)
            except NotFoundError:
                return None
            person = Person(**doc["_source"])
            await self._put_person_cache(person)
        return person

    async def _get_person_es_search(self, search_query: str, page: int, size: int) -> Optional[List[Person]]:
        from_ = get_es_from_value(page, size)
        query = {"multi_match": {"query": search_query, "fields": ["full_name"]}}
        
        cache_key = '-'.join(['persons', json.dumps(query), str(page), str(size)])
        
        persons = await self._get_list_persons_cache(cache_key)
        if not persons:
            try:
                matched = await self.elastic.search(index="persons", query=query, size=size, from_=from_)
            except NotFoundError:
                return None
            persons = [Person(**doc["_source"]) for doc in matched["hits"]["hits"]]
            await self._put_list_films_cache(cache_key, persons)
        return persons

    async def _get_person_cache(self, person_id: str) -> Optional[Person]:
        person_row = await self.redis.get('-'.join(['persons', person_id]))
        if not person_row:
            return None
        logging.info('Get person from cache')
        return Person.parse_raw(person_row)

    async def _put_person_cache(self, person: Person) -> None:
        logging.info('Save person to cache')
        await self.redis.set('-'.join(['persons', str(person.uuid)]), person.json(), ex=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_list_persons_cache(self, list_name: str) -> Optional[List[Person]]:
        persons_row = await self.redis.lrange(list_name, 0, -1)
        if not persons_row:
            return None
        logging.info('Get list persons from cache')
        return [Person.parse_raw(person_row) for person_row in persons_row]

    async def _put_list_films_cache(self, list_name: str, persons: List[Person]) -> None:
        logging.info('Save list persons to cache')
        await self.redis.lpush(list_name, *[person.json() for person in persons])
        await self.redis.expire(list_name, FILM_CACHE_EXPIRE_IN_SECONDS)



@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> PersonService:
    return PersonService(redis, elastic)
