from curses.ascii import EM

import pytest

from utils.server_messages import (
    EMPTY_QUERY_ERROR,
    MAX_LIMIT_PAGE_NUMBER_ERROR,
    MAX_LIMIT_PAGE_SIZE_ERROR,
    MIN_LIMIT_PAGE_NUMBER_ERROR,
    MIN_LIMIT_PAGE_SIZE_ERROR,
)
from utils.service import validate
from utils.structures import FilmBrief, Genre, Person

# Movies


@pytest.mark.asyncio
async def test_search_movies(make_get_request):
    response = await make_get_request("/films/search", {"query": "start"})
    assert response.status == 200
    validate(response.body, FilmBrief)


@pytest.mark.asyncio
async def test_search_movies_with_empty_query(make_get_request):
    response = await make_get_request("/films/search", {"query": ""})
    assert response.status == 422
    assert response.body == EMPTY_QUERY_ERROR


@pytest.mark.asyncio
async def test_search_movies_pagination(make_get_request):
    response = await make_get_request("/films/search", {"query": "start", "page[size]": 10000, "page[number]": 0})
    assert response.status == 200
    validate(response.body, FilmBrief)


@pytest.mark.asyncio
async def test_search_movies_by_valid_id_page_size_over_max_limit(make_get_request):
    response = await make_get_request("/films/search", {"query": "start", "page[size]": 10001, "page[number]": 0})
    assert response.status == 422
    assert response.body == MAX_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_search_movies_by_valid_id_page_size_over_min_limit(make_get_request):
    response = await make_get_request("/films/search", {"query": "start", "page[size]": 0, "page[number]": 0})
    assert response.status == 422
    assert response.body == MIN_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_search_movies_by_valid_id_page_number_over_min_limit(make_get_request):
    response = await make_get_request("/films/search", {"query": "start", "page[size]": 10, "page[number]": -1})
    assert response.status == 422
    assert response.body == MIN_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_search_movies_by_valid_id_page_number_over_max_limit(make_get_request, get_persons):
    response = await make_get_request("/films/search", {"query": "start", "page[size]": 10, "page[number]": 1000})
    assert response.status == 422
    assert response.body == MAX_LIMIT_PAGE_NUMBER_ERROR


# Genres


@pytest.mark.asyncio
async def test_search_genres(make_get_request):
    response = await make_get_request("/genres/search", {"query": "action"})
    assert response.status == 200
    validate(response.body, Genre)


@pytest.mark.asyncio
async def test_search_genres_with_empty_query(make_get_request):
    response = await make_get_request("/genres/search", {"query": ""})
    assert response.status == 422
    assert response.body == EMPTY_QUERY_ERROR


@pytest.mark.asyncio
async def test_search_genres_pagination(make_get_request):
    response = await make_get_request("/genres/search", {"query": "action", "page[size]": 10000, "page[number]": 0})
    assert response.status == 200
    validate(response.body, Genre)


@pytest.mark.asyncio
async def test_search_genres_by_valid_id_page_size_over_max_limit(make_get_request):
    response = await make_get_request("/genres/search", {"query": "action", "page[size]": 10001, "page[number]": 0})
    assert response.status == 422
    assert response.body == MAX_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_search_genres_by_valid_id_page_size_over_min_limit(make_get_request):
    response = await make_get_request("/genres/search", {"query": "action", "page[size]": 0, "page[number]": 0})
    assert response.status == 422
    assert response.body == MIN_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_search_genres_by_valid_id_page_number_over_min_limit(make_get_request):
    response = await make_get_request("/genres/search", {"query": "action", "page[size]": 10, "page[number]": -1})
    assert response.status == 422
    assert response.body == MIN_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_search_genres_by_valid_id_page_number_over_max_limit(make_get_request, get_persons):
    response = await make_get_request("/genres/search", {"query": "action", "page[size]": 10, "page[number]": 1000})
    assert response.status == 422
    assert response.body == MAX_LIMIT_PAGE_NUMBER_ERROR


# Persons


@pytest.mark.asyncio
async def test_search_persons(make_get_request):
    response = await make_get_request("/persons/search", {"query": "lucas"})
    assert response.status == 200
    validate(response.body, Person)


@pytest.mark.asyncio
async def test_search_persons_with_empty_query(make_get_request):
    response = await make_get_request("/persons/search", {"query": ""})
    assert response.status == 422
    assert response.body == EMPTY_QUERY_ERROR


@pytest.mark.asyncio
async def test_search_persons_pagination(make_get_request):
    response = await make_get_request("/persons/search", {"query": "lucas", "page[size]": 10000, "page[number]": 0})
    assert response.status == 200
    validate(response.body, Person)


@pytest.mark.asyncio
async def test_search_persons_by_valid_id_page_size_over_max_limit(make_get_request):
    response = await make_get_request("/persons/search", {"query": "lucas", "page[size]": 10001, "page[number]": 0})
    assert response.status == 422
    assert response.body == MAX_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_search_persons_by_valid_id_page_size_over_min_limit(make_get_request):
    response = await make_get_request("/persons/search", {"query": "lucas", "page[size]": 0, "page[number]": 0})
    assert response.status == 422
    assert response.body == MIN_LIMIT_PAGE_SIZE_ERROR


@pytest.mark.asyncio
async def test_search_persons_by_valid_id_page_number_over_min_limit(make_get_request):
    response = await make_get_request("/persons/search", {"query": "lucas", "page[size]": 10, "page[number]": -1})
    assert response.status == 422
    assert response.body == MIN_LIMIT_PAGE_NUMBER_ERROR


@pytest.mark.asyncio
async def test_search_persons_by_valid_id_page_number_over_max_limit(make_get_request, get_persons):
    response = await make_get_request("/persons/search", {"query": "lucas", "page[size]": 10, "page[number]": 1000})
    assert response.status == 422
    assert response.body == MAX_LIMIT_PAGE_NUMBER_ERROR
