from http import HTTPStatus

import pytest
from sqlalchemy import MetaData, create_engine, text

from tests.functional.fixtures.async_http import HTTPResponse
from tests.functional.settings import test_settings

USER = {
    "login": "validlogin",
    "email": "valid@ema.il",
    "password": "valid password",
}


@pytest.fixture(scope="session", autouse=True)
def db_delete_everything():
    def _delete(engine):
        # define the tables to delete
        table_names = [
            "jwt_store",
            "login_history",
            "user_role",
            "roles",
            "users",
        ]

        with engine.begin() as conn:
            for table in table_names:
                conn.execute(
                    text(f"TRUNCATE {table} RESTART IDENTITY CASCADE;")
                )

    engine = create_engine(test_settings.postgres_dsn)

    _delete(engine)
    yield
    _delete(engine)


@pytest.fixture
def register_user(aiohttp_post):
    async def inner(login, email, password):
        endpoint = "registration"
        payload = {"login": login, "email": email, "password": password}
        response = await aiohttp_post(endpoint, payload)
        return response

    return inner


@pytest.fixture(scope="session")
async def user(register_user):
    response = await register_user(**USER)
    return response


@pytest.fixture
def login_user(aiohttp_post):
    async def inner(login, password):
        endpoint = "login"
        payload = {"login": login, "password": password}
        response = await aiohttp_post(endpoint, payload)
        return response

    return inner


@pytest.fixture(scope="session")
async def logined_user(user, login_user):
    response = await login_user(login=USER["login"], password=USER["password"])
    return response


@pytest.mark.asyncio_cooperative
@pytest.mark.parametrize(
    "login, email, password, response_status, success",
    [
        (
            "bad login #1",
            "valid@ema.il",
            "qwe",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        (
            "validlogin",
            "not email",
            "qwe",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        (
            "validlogin",
            "valid@ema.il",
            "",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        (
            "validlogin",
            "valid@ema.il",
            "short",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        (*USER.values(), HTTPStatus.OK, True),
    ],
)
async def test_registration(
    login, email, password, response_status, success, register_user
) -> None:
    response = await register_user(login, email, password)
    assert response.status == response_status
    assert response.body.get("success") == success


@pytest.mark.asyncio_cooperative
@pytest.mark.parametrize(
    "login, password, response_status, success",
    [
        (USER["login"], USER["password"], HTTPStatus.OK, True),
        (
            "bad login #1",
            "qwe",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        (
            "validlogin",
            "qwe",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        (
            "validlogin",
            "",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        (
            "validlogin",
            "short",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
    ],
)
async def test_login(login, password, response_status, success) -> None:
    response = await login_user(login, password)
    assert response.status == response_status
    assert response.body.get("success") == success


@pytest.mark.asyncio_cooperative
@pytest.mark.parametrize(
    "token, refresh_token, response_status, success",
    [
        ("vv", "vv", HTTPStatus.OK, True),
        (
            "bad login #1",
            "dsgfdsg",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        # (
        #     "1241241414",
        #     "214",
        #     HTTPStatus.UNAUTHORIZED,
        #     False,
        # ),
    ],
)
async def test_logout(
    token, refresh_token, response_status, success, aiohttp_post, logined_user
) -> None:
    endpoint = "logout"
    body = {"refresh_token": refresh_token}
    token = token
    if success:
        data = logined_user.body["data"]
        body["refresh_token"] = data["refresh_token"]
        token = data["access_token"]
    response = await aiohttp_post(endpoint, body, token)
    assert response.status == response_status
    assert response.body.get("success") == success


@pytest.mark.asyncio_cooperative
@pytest.mark.parametrize(
    "token, refresh_token, response_status, success",
    [
        ("vv", "vv", HTTPStatus.OK, True),
        (
            "bad login #1",
            "dsgfdsg",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        # (
        #     "1241241414",
        #     "214",
        #     HTTPStatus.UNAUTHORIZED,
        #     False,
        # ),
    ],
)
async def test_logout_all(
    token, refresh_token, response_status, success, aiohttp_post, logined_user
) -> None:
    endpoint = "logout_all"
    body = {"refresh_token": refresh_token}
    token = token
    if success:
        data = logined_user.body["data"]
        body["refresh_token"] = data["refresh_token"]
        token = data["access_token"]
    response = await aiohttp_post(endpoint, body, token)
    assert response.status == response_status
    assert response.body.get("success") == success


@pytest.mark.asyncio_cooperative
@pytest.mark.parametrize(
    "token, response_status, success",
    [
        ("vv", HTTPStatus.OK, True),
        (
            "bad login #1",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            False,
        ),
        # (
        #     "1241241414",
        #     HTTPStatus.UNAUTHORIZED,
        #     False,
        # ),
    ],
)
async def test_refresh(
    token, refresh_token, response_status, success, aiohttp_post, logined_user
) -> None:
    endpoint = "refresh"
    body = {"refresh_token": refresh_token}
    token = token
    if success:
        data = logined_user.body["data"]
        body["refresh_token"] = data["refresh_token"]
        token = data["access_token"]
    response = await aiohttp_post(endpoint, body, token)
    assert response.status == response_status
    assert response.body.get("success") == success
