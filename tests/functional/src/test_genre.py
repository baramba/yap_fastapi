import logging
import os
from random import randint

import aioredis
import pytest

from utils.structures import Genre

log = logging.getLogger(os.path.basename(__file__))


@pytest.mark.asyncio
async def test_genres_extrem(make_get_request):
    response = await make_get_request("/genres?page[number]=-1&page[size]=10")
    assert response.status == 422

    not_valid_page_number = {
        "detail": [
            {
                "loc": ["query", "page[number]"],
                "msg": "ensure this value is greater than or equal to 0",
                "type": "value_error.number.not_ge",
                "ctx": {"limit_value": 0},
            }
        ]
    }
    assert not_valid_page_number == response.body


@pytest.mark.asyncio
async def test_genres_all(make_get_request):
    response = await make_get_request("/genres")
    assert response.status == 200
    assert len(response.body) == 10


@pytest.mark.asyncio
async def test_genres_one(make_get_request, get_genres):
    genre = get_genres[randint(0, len(get_genres))]
    response = await make_get_request("/genres/{0}".format(genre.uuid))
    assert response.status == 200
    assert response.body.get("uuid") == str(genre.uuid)
    response = await make_get_request("/genres/{0}".format("not correct uuid"))
    assert response.status == 422

    not_valid_value_uuid = {
        "detail": [
            {
                "loc": [
                    "path",
                    "genre_id",
                ],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            },
        ]
    }
    assert response.body == not_valid_value_uuid


@pytest.mark.asyncio
async def test_genres_all_cache(make_get_request, redis_client: aioredis.Redis):
    await redis_client.flushall()
    response = await make_get_request("/genres")
    assert response.status == 200
    keys = await redis_client.scan(count=10, match="*genre*")
    result = await redis_client.lrange(keys[1][0].decode(), 0, -1)
    genres_from_cache = [Genre.parse_raw(row) for row in result[::-1]]
    genres_from_api = [Genre(**row) for row in response.body]
    assert genres_from_api == genres_from_cache


@pytest.mark.asyncio
async def test_genres_one_cache(make_get_request, get_genres, redis_client: aioredis.Redis):
    await redis_client.flushall()
    genre = get_genres[randint(0, len(get_genres))]
    response = await make_get_request("/genres/{0}".format(genre.uuid))
    assert response.status == 200

    keys = await redis_client.scan(count=10, match="*genre*")
    result = await redis_client.get(keys[1][0].decode())
    genre_from_cache = Genre.parse_raw(result)
    genre_from_api = Genre(**response.body)
    assert genre_from_cache == genre_from_api
