from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "endpoint, search_query, num_results, first_result_id",
    [
        ("shows", "star", 100, "05d7341e-e367-4e2e-acf5-4652a8435f93"),
        (
            "shows",
            "Star Trek: Phoenix - No Other Medicine",
            100,
            "64733f2b-136d-4ed3-90d6-92d63247c6b0",
        ),
        ("shows", pytest.strange_unicode_str, 0, None),
        (
            "persons",
            "Václav Vorlícek",
            3,
            "6e429cff-c8a2-4d17-8b12-6532a8a1ac9b",
        ),
        ("persons", pytest.strange_unicode_str, 0, None),
        ("genres", "western", 1, "0b105f87-e0a5-45dc-8ce7-f8632088f390"),
        ("genres", "westerm", 1, "0b105f87-e0a5-45dc-8ce7-f8632088f390"),
        ("genres", pytest.strange_unicode_str, 0, None),
    ],
)
async def test_search_endpoints(
    endpoint, search_query, num_results, first_result_id, aiohttp_get
):
    endpoint = f"{endpoint}/search"
    query_data = {"page[size]": 100}
    if search_query:
        query_data["query"] = search_query

    response = await aiohttp_get(endpoint, query_data)
    assert response.status == HTTPStatus.OK
    assert len(response.body) == num_results
    if first_result_id:
        assert response.body[0]["id"] == first_result_id
