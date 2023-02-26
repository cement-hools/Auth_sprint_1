import random
from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


async def test_get_all_persons(aiohttp_get) -> None:
    response = await aiohttp_get("persons")
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 10


@pytest.mark.parametrize("person_id", ["not-existent-id", 1, None])
async def test_persons_non_existing(person_id, aiohttp_get) -> None:
    endpoint = f"persons/{person_id}"
    response = await aiohttp_get(endpoint)
    assert response.status == HTTPStatus.NOT_FOUND


async def test_check_persons_on_different_page_size(aiohttp_get) -> None:
    endpoint = "persons"
    page_size = 16
    query_data = {
        "page[size]": page_size,
        "page[number]": 3,
    }
    response = await aiohttp_get(endpoint, query_data)
    assert response.status == HTTPStatus.OK
    assert len(response.body) == page_size

    person_on_first_page = response.body[0]
    query_data["page[number]"] += 1
    response = await aiohttp_get(endpoint, query_data)
    assert response.status == HTTPStatus.OK
    assert person_on_first_page not in response.body


async def test_search_person(aiohttp_get, es_client) -> None:
    data = es_client.search(index="persons")
    for person in random.sample(data["hits"]["hits"], 10):
        person_name = person["_source"]["full_name"]
        person_id = person["_source"]["id"]
        query = {"query": person_name}
        response = await aiohttp_get("persons/search", query)
        assert response.status == HTTPStatus.OK
        assert response.body[0]["full_name"] == person_name
        assert response.body[0]["id"] == person_id
