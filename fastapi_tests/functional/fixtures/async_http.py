from dataclasses import dataclass

import aiohttp
import pytest
from functional.settings import test_settings
from multidict import CIMultiDictProxy


@dataclass
class HTTPResponse:
    status: int
    headers: CIMultiDictProxy[str]
    body: str


@pytest.fixture(scope="session")
async def aiohttp_client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def aiohttp_get(aiohttp_client_session):
    async def inner(
        endpoint: str,
        query: dict = None,
    ):
        url = f"{test_settings.api_service_url}{test_settings.api_v1_base_path}{endpoint}"
        async with aiohttp_client_session.get(url, params=query) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return HTTPResponse(status=status, headers=headers, body=body)

    return inner
