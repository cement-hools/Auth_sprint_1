from http import HTTPStatus

import pytest


@pytest.mark.asyncio_cooperative
async def test_login_ok(aiohttp_get) -> None:
    endpoint = "login"

    response = await aiohttp_get(endpoint)
    assert response.status == HTTPStatus.OK
