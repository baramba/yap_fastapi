import asyncio
import json
import logging
import os
from typing import AsyncGenerator, Optional

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from config.settings import settings
from src.response import HTTPResponse
from utils.structures import Film, Genre, Person
from utils.testdata import read_testdata

log = logging.getLogger(os.path.basename(__file__))


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


async def create_es_index(es_client: AsyncElasticsearch, index: str, filename: str):
    with open(os.path.join(settings.testdata, filename)) as file:
        es_schema = json.load(file)

        await es_client.indices.create(index=index, mappings=es_schema["mappings"], settings=es_schema["settings"])


async def load_data_to_es(es_client: AsyncElasticsearch, index: str, filename: str):
    with open(os.path.join(settings.testdata, filename)) as file:
        es_data = json.load(file)
    actions = [
        {
            "_index": index,
            "_id": data["_id"],
            "_source": {key: value for key, value in data.items() if key not in ("_id", "_score", "_index")},
        }
        for data in es_data["hits"]["hits"]
    ]
    await async_bulk(client=es_client, actions=actions)


@pytest.mark.asyncio
@pytest.fixture(scope="session", autouse=True)
async def config_test_env(es_client: AsyncElasticsearch):
    log.info("make config_test_env")
    for index, files in settings.es_schema.items():
        if not await es_client.indices.exists(index=index):
            await create_es_index(es_client, index, filename=files["sch_file"])
            await load_data_to_es(es_client=es_client, index=index, filename=files["data_file"])


@pytest.fixture(scope="session")
def get_genres():
    genres: list = read_testdata(settings.es_schema["genres"]["data_file"])
    return [Genre(**genre) for genre in genres]


@pytest.fixture(scope="session")
def get_persons():
    persons: list = read_testdata(settings.es_schema["persons"]["data_file"])
    return [Person(**person) for person in persons]


@pytest.fixture(scope="session")
def get_movies():
    movies: list = read_testdata(settings.es_schema["movies"]["data_file"])
    return [Film(**movie) for movie in movies]


@pytest.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(hosts=settings.es)
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    client = await aioredis.from_url(settings.redis_dsn)
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def http_client():
    client = aiohttp.ClientSession()
    yield client
    await client.close()


@pytest.fixture
async def redis_flush(redis_client):
    redis_client.flushall()


@pytest.fixture
def make_get_request(http_client):
    async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}

        url = "{0}{1}".format(settings.api_url, method)
        try:
            async with http_client.get(url, params=params) as response:
                return HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )
        except Exception as e:
            logging.error(e)

    return inner
