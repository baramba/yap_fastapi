import json
import os
from typing import AsyncGenerator

import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from config.settings import settings


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

    for index, files in settings.es_schema.items():
        if not await es_client.indices.exists(index=index):
            await create_es_index(es_client, index, filename=files["sch_file"])
            await load_data_to_es(es_client=es_client, index=index, filename=files["data_file"])


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
