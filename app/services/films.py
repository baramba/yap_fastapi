import json
import logging
import uuid
from functools import lru_cache
from http import HTTPStatus
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from db.elastic import get_elastic
from db.redis import get_redis
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from models.film import Film
from services.service_utils import get_es_from_value

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService(object):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: uuid.UUID) -> Optional[Film]:
        film = await self._film_cache(str(film_id))
        if not film:
            film = await self._get_film_es(film_id)
            if not film:
                return None
            await self._put_film_cache(film)

        return film

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

        cache_key = '-'.join(['movies', json.dumps(query), sort, str(page), str(size)])

        films = await self._list_films_cache(cache_key)
        if not films:
            films = []
            from_ = get_es_from_value(page, size)

            try:
                matched_docs = await self.elastic.search(index="movies", query=query, sort=sort, size=size, from_=from_)
            except NotFoundError:
                return None

            for doc in matched_docs["hits"]["hits"]:
                films.append(Film(**doc["_source"]))
            
            await self._put_list_films_cache(cache_key, films)

        return films

    async def get_films_search(
        self,
        search_query: str,
        page: int = 0,
        size: int = 1,
    ) -> Optional[List[Film]]:
        query = {"multi_match": {"query": search_query, "fields": ["title", "description"]}}

        cache_key = '-'.join(['movies', json.dumps(query), str(page), str(size)])

        films = await self._list_films_cache(cache_key)
        if not films:
            films = []
            from_ = get_es_from_value(page, size)
            try:
                matched_docs = await self.elastic.search(index="movies", query=query, size=size, from_=from_)
            except NotFoundError:
                return None
            for doc in matched_docs["hits"]["hits"]:
                films.append(Film(**doc["_source"]))
            await self._put_list_films_cache(cache_key, films)
        return films

    async def _get_film_es(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        logging.info('Get from Elasticsearch')    
        return Film(**doc["_source"])

    async def _film_cache(self, film_id: str) -> Optional[Film]:
        film_row = await self.redis.get('-'.join(['movies', film_id]))
        if not film_row:
            return None

        logging.info('Get from cache')
        return Film.parse_raw(film_row)

    async def _list_films_cache(self, list_name: str) -> Optional[List[Film]]:
        films_row = await self.redis.lrange(str(list_name), 0, -1)
        if not films_row:
            return None

        logging.info('Get list from cache')
        return [Film.parse_raw(film_row) for film_row in films_row]

    async def _put_film_cache(self, film: Film):
        logging.info('Save film to cache')
        await self.redis.set('-'.join(['movies', str(film.uuid)]), film.json(), ex=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _put_list_films_cache(self, list_name: str, films: List[Film]):
        logging.info('Save films list to cache')
        await self.redis.lpush(list_name, *[film.json() for film in films])


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),  # type: ignore
    elastic: AsyncElasticsearch = Depends(get_elastic),  # type: ignore
) -> FilmService:
    return FilmService(redis, elastic)
