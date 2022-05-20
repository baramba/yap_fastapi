import uuid
from functools import lru_cache
from typing import Optional

from services.base import BaseSearch
from services.cache import cache
from services.elastic import Elastic
from services.service_utils import get_offset

from fastapi.params import Depends


class GenreService:
    def __init__(self, search: BaseSearch):
        self.search = search

    @cache
    async def get_genres(self, size: int, page: int) -> Optional[list[dict]]:
        offset = get_offset(page, size)
        res = await self.search.search(index='genres', size=size, offset=offset)
        print('### get_genres:\n', res)
        return res

    @cache
    async def get_genres_search(self, search_query: str, size: int, page: int) -> Optional[list[dict]]:
        offset = get_offset(page, size)
        res = await self.search.search(index='genres', size=size, offset=offset, search_query=search_query)
        return res

    @cache
    async def get_genre(self, genre_id: uuid.UUID) -> Optional[dict]:
        res = await self.search.get(index="genres", id=str(genre_id))
        return res


@lru_cache()
def get_genre_service(
    search: BaseSearch = Depends(Elastic),  # type: ignore
) -> GenreService:
    return GenreService(search)
