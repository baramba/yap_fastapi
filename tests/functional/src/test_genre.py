from http import HTTPStatus
from random import choice

import aioredis
import pytest

from utils.server_messages import (
    GENRE_UUID_ERROR,
    MAX_LIMIT_PAGE_NUMBER_ERROR,
    MAX_LIMIT_PAGE_SIZE_ERROR,
    MIN_LIMIT_PAGE_NUMBER_ERROR,
    MIN_LIMIT_PAGE_SIZE_ERROR,
)
from utils.service import validate
from utils.structures import Genre


async def test_genres_all(make_get_request):
    response = await make_get_request("/genres")
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 10
    validate(response.body, Genre)


@pytest.mark.asyncio
async def test_genres_by_valid_id(make_get_request, get_genres):
    genre = choice(get_genres)
    response = await make_get_request("/genres/{id}".format(id=genre.uuid))
    assert response.status == HTTPStatus.OK
    validate(response.body, Genre)
    assert response.body.get("uuid") == str(genre.uuid)


@pytest.mark.asyncio
async def test_genres_by_not_valid_id(make_get_request):
    response = await make_get_request("/genres/{id}".format(id="not correct uuid"))
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == GENRE_UUID_ERROR


@pytest.mark.asyncio
async def test_genres_pagination(make_get_request):
    response = await make_get_request("/genres", {"page[size]": 10000, "page[number]": 0})
    assert response.status == HTTPStatus.OK
    validate(response.body, Genre)


@pytest.mark.asyncio
async def test_genres_pagination_page_size_over_max_limit(make_get_request):
    response = await make_get_request("/genres", {"page[size]": 10001, "page[number]": 0})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MAX_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_genres_pagination_page_size_over_min_limit(make_get_request):
    response = await make_get_request("/genres", {"page[size]": 0, "page[number]": 0})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MIN_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_genres_pagination_page_number_over_min_limit(make_get_request):
    response = await make_get_request("/genres", {"page[size]": 10, "page[number]": -1})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MIN_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_genres_pagination_page_number_over_max_limit(make_get_request):
    response = await make_get_request("/genres", {"page[size]": 10, "page[number]": 1000})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MAX_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_genres_search(make_get_request, redis_client: aioredis.Redis, get_genres: list[Genre]):
    await redis_client.flushall()
    genre = choice(get_genres)
    response = await make_get_request("/genres/search", {"query": genre.name})
    assert response.status == HTTPStatus.OK
    keys = await redis_client.scan(count=10, match="*genre*")
    cache = await redis_client.lrange(keys[1][0].decode(), 0, -1)
    assert sorted(validate(response.body, Genre)) == sorted(validate(cache, Genre))


@pytest.mark.asyncio
async def test_genres_all_cache(make_get_request, redis_client: aioredis.Redis):
    await redis_client.flushall()
    response = await make_get_request("/genres")
    assert response.status == HTTPStatus.OK
    keys = await redis_client.scan(count=10, match="*genre*")
    cache = await redis_client.lrange(keys[1][0].decode(), 0, -1)
    assert sorted(validate(response.body, Genre)) == sorted(validate(cache, Genre))


@pytest.mark.asyncio
async def test_genres_by_valid_id_cache(make_get_request, get_genres, redis_client: aioredis.Redis):
    await redis_client.flushall()
    genre = choice(get_genres)
    response = await make_get_request("/genres/{id}".format(id=genre.uuid))
    assert response.status == HTTPStatus.OK
    keys = await redis_client.scan(count=10, match="*genre*")
    cache = await redis_client.get(keys[1][0].decode())
    assert validate(response.body, Genre) == validate(cache, Genre)
