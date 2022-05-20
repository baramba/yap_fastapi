import uuid
from functools import lru_cache
from typing import Optional

from services.base import BaseSearch
from services.cache import cache
from services.elastic import Elastic
from services.service_utils import get_offset

from fastapi.params import Depends


class FilmService:
    def __init__(self, search: BaseSearch):
        self.search = search

    @cache
    async def get_by_id(self, film_id: str) -> Optional[dict]:
        res = await self.search.get(index='movies', id=film_id)
        return res

    @cache
    async def get_films(
        self,
        sort: str,
        size: int = 1,
        page: int = 0,
        genre: Optional[uuid.UUID] = None,
    ) -> Optional[list[dict]]:

        offset = get_offset(page, size)

        res = await self.search.search(index="movies", size=size, offset=offset, genre=genre, sort=sort)
        return res

    @cache
    async def get_films_search(
        self,
        search_query: str,
        page: int = 0,
        size: int = 1,
    ) -> Optional[list[dict]]:

        offset = get_offset(page, size)

        res = await self.search.search(index="movies", size=size, offset=offset, search_query=search_query)
        return res


@lru_cache()
def get_film_service(
    search: BaseSearch = Depends(Elastic),  # type: ignore
) -> FilmService:
    return FilmService(search)
