import random
from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


async def test_get_all_genres(aiohttp_get) -> None:
    response = await aiohttp_get('genres')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 10


@pytest.mark.parametrize(
    'genre_id',
    [
        'not-existent-id',
        1,
        None
     ]
)
async def test_genres_non_existing(genre_id, aiohttp_get) -> None:
    endpoint = f'genres/{genre_id}'
    response = await aiohttp_get(endpoint)
    assert response.status == HTTPStatus.NOT_FOUND


async def test_search_genre_from_es_and_api(aiohttp_get, es_client) -> None:
    data = es_client.search(index='genres')
    for genre in random.sample(data['hits']['hits'], 10):
        genre_name = genre['_source']['name']
        genre_id = genre['_source']['id']
        response = await aiohttp_get(f'genres/{genre_id}')
        assert response.status == HTTPStatus.OK
        assert response.body['name'] == genre_name
        assert response.body['id'] == genre_id
