import uuid
from functools import lru_cache
from typing import Optional

from services.base import BaseSearch
from services.cache import cache
from services.elastic import Elastic
from services.service_utils import get_offset

from fastapi.params import Depends


class PersonService:
    def __init__(self, search: BaseSearch):
        self.search = search

    @cache
    async def get_person(self, person_id: uuid.UUID) -> Optional[dict]:
        res = await self.search.get(index="persons", id=str(person_id))
        return res

    @cache
    async def get_persons_search(self, search_query: str, size: int, page: int) -> Optional[list[dict]]:
        offset = get_offset(page, size)
        res = await self.search.search(index='persons', size=size, offset=offset, search_query=search_query)
        return res

    @cache
    async def get_films_by_person(self, person_id: uuid.UUID, size: int, page: int) -> Optional[list[dict]]:
        offset = get_offset(page, size)
        res = await self.search.search(index='movies', size=size, offset=offset, person_id=person_id)
        return res


@lru_cache()
def get_person_service(
    search: BaseSearch = Depends(Elastic),  # type: ignore
) -> PersonService:
    return PersonService(search)
