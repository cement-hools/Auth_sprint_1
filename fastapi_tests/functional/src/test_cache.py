import asyncio
from http import HTTPStatus

import pytest

from fastapi_tests.functional.settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_shows_show_id_cache(aiohttp_get, es_async_client, restore_indexes_after) -> None:
    show_id = '00af52ec-9345-4d66-adbe-50eb917f463a'
    endpoint = f'shows/{show_id}'

    response = await aiohttp_get(endpoint)
    assert response.status == HTTPStatus.OK
    assert response.body['id'] == show_id

    await es_async_client.delete(index=test_settings.show_index_name, id=show_id)

    response = await aiohttp_get(endpoint)
    assert response.status == HTTPStatus.OK
    assert response.body['id'] == show_id


async def test_persons_cache_pass(aiohttp_get, es_async_client, restore_indexes_after) -> None:
    person_id = '6e429cff-c8a2-4d17-8b12-6532a8a1ac9b'
    endpoint = f'persons/{person_id}'
    response = await aiohttp_get(endpoint)
    assert response.body['id'] == person_id

    await es_async_client.delete(index=test_settings.person_index_name, id=person_id)

    response = await aiohttp_get(endpoint)
    assert response.body['id'] == person_id


async def test_genres_cache_pass(aiohttp_get, es_async_client, restore_indexes_after) -> None:
    genre_id = '526769d7-df18-4661-9aa6-49ed24e9dfd8'
    endpoint = f'genres/{genre_id}'
    response = await aiohttp_get(endpoint)
    assert response.body['id'] == genre_id

    await es_async_client.delete(index=test_settings.genre_index_name, id=genre_id)

    response = await aiohttp_get(endpoint)
    assert response.body['id'] == genre_id


async def test_persons_cache_expiration(
        aiohttp_get, es_async_client, restore_indexes_after
) -> None:
    person_id = '6e429cff-c8a2-4d17-8b12-6532a8a1ac9b'
    endpoint = f'persons/{person_id}'
    response = await aiohttp_get(endpoint)
    assert response.body['id'] == person_id

    await es_async_client.delete(index=test_settings.person_index_name, id=person_id)
    await asyncio.sleep(5)

    with pytest.raises(KeyError):
        response = await aiohttp_get(endpoint)
        assert response.body['id'] == person_id


async def test_genres_cache_expiration(
        aiohttp_get, es_async_client, restore_indexes_after
) -> None:
    genre_id = '5373d043-3f41-4ea8-9947-4b746c601bbd'
    endpoint = f'genres/{genre_id}'
    response = await aiohttp_get(endpoint)
    assert response.body['id'] == genre_id

    await es_async_client.delete(index=test_settings.genre_index_name, id=genre_id)
    await asyncio.sleep(5)

    with pytest.raises(KeyError):
        response = await aiohttp_get(endpoint)
        assert response.body['id'] == genre_id
