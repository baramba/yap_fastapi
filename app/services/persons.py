import uuid
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from db.redis import get_redis
from services.base import BaseSearch
from services.cache import cache2
from services.elastic import Elastic
from services.service_utils import get_offset

from fastapi.params import Depends

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, search: BaseSearch):
        self.redis = redis
        self.search = search

    @cache2
    async def get_person(self, person_id: uuid.UUID) -> Optional[dict]:
        res = await self.search.get(index="persons", id=str(person_id))
        return res

    @cache2
    async def get_persons_search(self, search_query: str, size: int, page: int) -> Optional[list[dict]]:
        offset = get_offset(page, size)
        res = await self.search.search(index='persons', size=size, offset=offset, search_query=search_query)
        return res

    @cache2
    async def get_films_by_person(self, person_id: uuid.UUID, size: int, page: int) -> Optional[list[dict]]:
        offset = get_offset(page, size)
        res = await self.search.search(index='movies', size=size, offset=offset, person_id=person_id)
        return res


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    search: BaseSearch = Depends(Elastic),  # type: ignore
) -> PersonService:
    return PersonService(redis, search)
