from http import HTTPStatus
from random import choice

import aioredis
import pytest

from utils.server_messages import (
    FILM_UUID_ERROR,
    FILTER_GENRE_UUID_ERROR,
    MAX_LIMIT_PAGE_NUMBER_ERROR,
    MAX_LIMIT_PAGE_SIZE_ERROR,
    MIN_LIMIT_PAGE_NUMBER_ERROR,
    MIN_LIMIT_PAGE_SIZE_ERROR,
    SORT_ERROR,
)
from utils.service import validate
from utils.structures import Film, FilmBrief


@pytest.mark.asyncio
async def test_movies_all(make_get_request, get_movies_brief):
    response = await make_get_request("/films")
    assert response.status == HTTPStatus.OK
    expected_films = get_movies_brief[:-11:-1]  # default sort = _doc:desc; page[size] = 10
    assert validate(response.body, FilmBrief) == expected_films


@pytest.mark.asyncio
async def test_movies_with_valid_sort(make_get_request, get_movies_brief):
    response = await make_get_request("/films", {"sort": "-imdb_rating"})
    assert response.status == HTTPStatus.OK
    expected_films = sorted(get_movies_brief, key=lambda item: item.imdb_rating,
                            reverse=True)[:10]  # default page[size] = 10
    assert validate(response.body, FilmBrief) == expected_films


@pytest.mark.asyncio
async def test_movies_with_not_valid_sort(make_get_request):
    response = await make_get_request("/films", {"sort": ""})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == SORT_ERROR


@pytest.mark.asyncio
async def test_movies_pagination(make_get_request, get_movies_brief):
    response = await make_get_request("/films", {"page[size]": 10000, "page[number]": 0})
    assert response.status == HTTPStatus.OK
    expected_films = get_movies_brief[:-10001:-1]
    assert validate(response.body, FilmBrief) == expected_films


@pytest.mark.asyncio
async def test_movies_pagination_page_size_over_max_limit(make_get_request):
    response = await make_get_request("/films", {"page[size]": 10001, "page[number]": 0})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MAX_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_movies_pagination_page_size_over_min_limit(make_get_request):
    response = await make_get_request("/films", {"page[size]": 0, "page[number]": 0})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MIN_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_movies_pagination_page_number_over_min_limit(make_get_request):
    response = await make_get_request("/films", {"page[size]": 10, "page[number]": -1})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MIN_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_movies_pagination_page_number_over_max_limit(make_get_request):
    response = await make_get_request("/films", {"page[size]": 10, "page[number]": 1000})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == MAX_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_movies_with_valid_filter(make_get_request, get_genres, get_movies):
    genre = choice(get_genres)
    expected_films = [
        film.copy(include={'uuid', 'imdb_rating', 'title'})
        for film in get_movies
        if str(genre.uuid) in [film_genre['uuid'] for film_genre in film.genre]
    ][:-11:-1]
    response = await make_get_request("/films", {"filter[genre]": str(genre.uuid)})
    if len(expected_films) > 0:
        assert response.status == HTTPStatus.OK
        assert validate(response.body, FilmBrief) == expected_films
    else:
        assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_movies_with_not_valid_filter(make_get_request, get_genres):
    genre = choice(get_genres)
    response = await make_get_request("/films", {"filter[genre]": ""})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == FILTER_GENRE_UUID_ERROR


@pytest.mark.asyncio
async def test_movies_by_valid_id(make_get_request, get_movies):
    movie = choice(get_movies)
    response = await make_get_request("/films/{id}".format(id=movie.uuid))
    assert response.status == HTTPStatus.OK
    assert validate(response.body, Film) == movie


@pytest.mark.asyncio
async def test_movies_by_not_valid_id(make_get_request):
    response = await make_get_request("/films/Star_wars")
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body == FILM_UUID_ERROR


@pytest.mark.asyncio
async def test_movies_by_valid_id_cache(make_get_request, get_movies, redis_client: aioredis.Redis):
    await redis_client.flushall()
    movie = choice(get_movies)
    response = await make_get_request("/films/{id}".format(id=movie.uuid))
    assert response.status == HTTPStatus.OK
    keys = await redis_client.scan(count=10, match="*by_id*")
    cache = await redis_client.get(keys[1][0].decode())
    assert validate(response.body, Film) == validate(cache, Film)


@pytest.mark.asyncio
async def test_movies_all_cache(make_get_request, redis_client: aioredis.Redis):
    await redis_client.flushall()
    response = await make_get_request("/films")
    assert response.status == HTTPStatus.OK
    keys = await redis_client.scan(count=10, match="*films*")
    cache = await redis_client.lrange(keys[1][0].decode(), 0, -1)
    assert sorted(validate(response.body, FilmBrief)) == sorted(validate(cache, FilmBrief))
