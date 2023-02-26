from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


async def test_shows_root(aiohttp_get) -> None:
    endpoint = "shows"
    response = await aiohttp_get(endpoint)
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 10


async def test_shows_get_concrete_show(aiohttp_get) -> None:
    show_id = "00af52ec-9345-4d66-adbe-50eb917f463a"
    endpoint = f"shows/{show_id}"
    response = await aiohttp_get(endpoint)
    assert response.status == HTTPStatus.OK
    assert response.body["id"] == show_id


async def test_shows_non_existing(aiohttp_get) -> None:
    show_id = "not-existent-id"
    endpoint = f"shows/{show_id}"
    response = await aiohttp_get(endpoint)
    assert response.status == HTTPStatus.NOT_FOUND


async def test_shows_pagination(aiohttp_get) -> None:
    endpoint = "shows"
    page_size = 16
    query_data = {
        "page[size]": page_size,
        "page[number]": 3,
    }
    response = await aiohttp_get(endpoint, query_data)
    assert response.status == HTTPStatus.OK
    # Check that page[size] parameter changes number of shows per page
    assert len(response.body) == page_size

    # Check that there are different shows on different pages
    show_on_first_page = response.body[0]
    query_data["page[number]"] += 1
    response = await aiohttp_get(endpoint, query_data)
    assert response.status == HTTPStatus.OK
    assert show_on_first_page not in response.body


@pytest.mark.parametrize(
    "query, sort, page_size, page_number, response_status",
    [
        (None, None, None, None, HTTPStatus.OK),
        # sort
        ("", None, None, None, HTTPStatus.OK),
        (None, "imdb_rating", None, None, HTTPStatus.OK),
        (None, "-imdb_rating", None, None, HTTPStatus.OK),
        (None, "+imdb_rating", None, None, HTTPStatus.OK),
        (None, "+-imdb_rating", None, None, HTTPStatus.BAD_REQUEST),
        (None, "-+imdb_rating", None, None, HTTPStatus.BAD_REQUEST),
        (None, "imdb_rating-", None, None, HTTPStatus.BAD_REQUEST),
        (None, "imdb_rating+", None, None, HTTPStatus.BAD_REQUEST),
        (None, "", None, None, HTTPStatus.BAD_REQUEST),
        (
            None,
            "non-existing-field-to-sort",
            None,
            None,
            HTTPStatus.BAD_REQUEST,
        ),
        # page[size]
        (None, None, 1, None, HTTPStatus.OK),
        (None, None, 10000000, None, HTTPStatus.UNPROCESSABLE_ENTITY),
        (None, None, -1, None, HTTPStatus.UNPROCESSABLE_ENTITY),
        (None, None, 0, None, HTTPStatus.UNPROCESSABLE_ENTITY),
        (None, None, "text", None, HTTPStatus.UNPROCESSABLE_ENTITY),
        # page[number]
        (None, None, None, 5, HTTPStatus.OK),
        (None, None, 10000, 5, HTTPStatus.UNPROCESSABLE_ENTITY),
        (None, None, None, -5, HTTPStatus.UNPROCESSABLE_ENTITY),
        (None, None, None, 0, HTTPStatus.UNPROCESSABLE_ENTITY),
        (None, None, None, "text", HTTPStatus.UNPROCESSABLE_ENTITY),
        # short happy path
        ("Tom", "-imdb_rating", 5, 5, HTTPStatus.OK),
    ],
)
async def test_shows_params_validation(
    query, sort, page_size, page_number, response_status, aiohttp_get
) -> None:
    endpoint = "shows"
    query_data = {}
    if query is not None:
        query_data["query"] = query
    if sort is not None:
        query_data["sort"] = sort
    if page_size is not None:
        query_data["page[size]"] = page_size
    if page_number is not None:
        query_data["page[number]"] = page_number

    response = await aiohttp_get(endpoint, query_data)
    assert response.status == response_status
