from dataclasses import dataclass

import aiohttp
import pytest
import requests
from multidict import CIMultiDictProxy

from tests.functional.settings import test_settings


@dataclass
class HTTPResponse:
    status: int
    headers: CIMultiDictProxy[str]
    body: str


@pytest.fixture(scope="session")
def client_session(request):
    session = requests.session()
    yield session
    session.close()


@pytest.fixture
def http_get(client_session):
    def inner(
        endpoint: str,
        query: dict = None,
        token: str = None,
    ):
        url = f"{test_settings.api_service_url}{test_settings.api_v1_base_path}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}
        with client_session.get(url, params=query, headers=headers) as response:
            body = response.json()
            headers = response.headers
            status = response.status_code
        return HTTPResponse(status=status, headers=headers, body=body)

    return inner


@pytest.fixture
def http_post(client_session):
    def inner(
        endpoint: str,
        json: str = None,
        token: str = None,
    ):
        url = f"{test_settings.api_service_url}{test_settings.api_v1_base_path}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}
        with client_session.post(
            url, json=json, headers=headers
        ) as response:
            body = response.json()
            headers = response.headers
            status = response.status_code
        return HTTPResponse(status=status, headers=headers, body=body)

    return inner
