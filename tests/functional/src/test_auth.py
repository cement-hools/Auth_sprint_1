import asyncio
from http import HTTPStatus

import pytest
from sqlalchemy import MetaData, create_engine, text

from tests.functional.fixtures.async_http import HTTPResponse
from tests.functional.settings import test_settings


USER = {"login": "admin", "password": "admin23432", "email": "upc@example.com"}

@pytest.fixture(scope="function", autouse=True)
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
def register_user(http_post):
    def inner(login, email, password):
        endpoint = "registration"
        payload = {"login": login, "email": email, "password": password}
        response = http_post(endpoint, payload)
        return response

    return inner


@pytest.fixture
def user(register_user):
    response = register_user(**USER)
    return response


@pytest.fixture
def user_logined(user, login_user):
    response = login_user(USER["login"], USER["password"])
    return response


@pytest.fixture
def login_user(http_post):
    def inner(login, password):
        endpoint = "login"
        payload = {"login": login, "password": password}
        response = http_post(endpoint, payload)
        return response

    return inner


@pytest.fixture
def logout_user(http_post):
    def inner(refresh_token, token):
        endpoint = "logout"
        payload = {"refresh_token": refresh_token}
        response = http_post(endpoint, payload, token)
        return response

    return inner
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
        ("validlogin", "valid@ema.il", "valid password", HTTPStatus.OK, True),
    ],
)
def test_registration(
    login, email, password, response_status, success, register_user
) -> None:
    response = register_user(login, email, password)
    assert response.status == response_status
    assert response.body.get("success") == success


@pytest.mark.parametrize(
    "login, password, response_status, success",
    [
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
        ("validlogin", "valid password", HTTPStatus.UNAUTHORIZED, False),
        (USER["login"], USER["password"], HTTPStatus.OK, True),
    ],
)
def test_login(
    login, password, response_status, success, login_user, user) -> None:
    response = login_user(login, password)
    assert response.status == response_status
    assert response.body.get("success") == success


@pytest.mark.parametrize(
    "refresh_token, token, response_status, success",
    [
        ("validlogin", "valid password", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        (USER["login"], USER["password"], HTTPStatus.OK, True),
    ],
)
def test_logout(
    refresh_token, token, response_status, success, user_logined, logout_user
) -> None:

    if success:
        refresh_token = user_logined.body["data"].get("refresh_token")
        token = user_logined.body["data"].get("access_token")
    response = logout_user(refresh_token, token)
    assert response.status == response_status
