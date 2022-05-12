from http import HTTPStatus
from random import choice

import aioredis
import pytest

from utils.server_messages import (
    MAX_LIMIT_PAGE_NUMBER_ERROR,
    MAX_LIMIT_PAGE_SIZE_ERROR,
    MIN_LIMIT_PAGE_NUMBER_ERROR,
    MIN_LIMIT_PAGE_SIZE_ERROR,
    PERSON_UUID_ERROR,
)
from utils.service import validate
from utils.structures import FilmBrief, Person


@pytest.mark.asyncio
async def test_persons_by_valid_id(make_get_request, get_persons):
    person = choice(get_persons)
    response = await make_get_request("/persons/{id}".format(id=person.uuid))
    assert response.status == HTTPStatus.OK
    validate(response.body, Person)


@pytest.mark.asyncio
async def test_persons_by_not_valid_id(make_get_request):
    response = await make_get_request("/persons/Lucas")
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == PERSON_UUID_ERROR


@pytest.mark.asyncio
async def test_films_with_person_by_valid_id(make_get_request, get_persons):
    person = choice(get_persons)
    response = await make_get_request("/persons/{id}/film".format(id=person.uuid))
    assert response.status == HTTPStatus.OK
    validate(response.body, FilmBrief)


@pytest.mark.asyncio
async def test_films_with_person_pagination(make_get_request, get_persons):
    person = choice(get_persons)
    response = await make_get_request(
        "/persons/{id}/film".format(id=person.uuid), {"page[size]": 10000, "page[number]": 0}
    )
    assert response.status == HTTPStatus.OK
    validate(response.body, FilmBrief)


@pytest.mark.asyncio
async def test_films_with_person_by_valid_id_page_size_over_max_limit(make_get_request, get_persons):
    person = choice(get_persons)
    response = await make_get_request(
        "/persons/{id}/film".format(id=person.uuid), {"page[size]": 10001, "page[number]": 0}
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MAX_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_films_with_person_by_valid_id_page_size_over_min_limit(make_get_request, get_persons):
    person = choice(get_persons)
    response = await make_get_request("/persons/{id}/film".format(id=person.uuid), {"page[size]": 0, "page[number]": 0})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MIN_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_films_with_person_by_valid_id_page_number_over_min_limit(make_get_request, get_persons):
    person = choice(get_persons)
    response = await make_get_request(
        "/persons/{id}/film".format(id=person.uuid), {"page[size]": 10, "page[number]": -1}
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MIN_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_films_with_person_by_valid_id_page_number_over_max_limit(make_get_request, get_persons):
    person = choice(get_persons)
    response = await make_get_request(
        "/persons/{id}/film".format(id=person.uuid), {"page[size]": 10, "page[number]": 1000}
    )
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MAX_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_persons_by_valid_id_cache(make_get_request, get_persons, redis_client: aioredis.Redis):
    await redis_client.flushall()
    person = choice(get_persons)
    response = await make_get_request("/persons/{id}".format(id=person.uuid))
    assert response.status == HTTPStatus.OK
    keys = await redis_client.scan(count=10, match="*person*")
    cache = await redis_client.get(keys[1][0].decode())
    assert validate(response.body, Person) == validate(cache, Person)
