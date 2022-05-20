import asyncio
from dataclasses import dataclass
from typing import Optional

import aiohttp
import pytest
from multidict import CIMultiDictProxy

from config.settings import settings

pytest_plugins = ("create_test_env", "get_test_data")


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


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
        async with http_client.get(url, params=params) as response:
            status = response.status
            body = await response.json() if status < 500 else {}
            headers = response.headers
            return HTTPResponse(body, headers, status)

    return inner
