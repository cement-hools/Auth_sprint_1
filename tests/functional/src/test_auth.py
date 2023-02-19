import asyncio
from http import HTTPStatus

import pytest
from sqlalchemy import MetaData, create_engine, text

from tests.functional.fixtures.async_http import HTTPResponse
from tests.functional.settings import test_settings

USER = {"login": "admin", "password": "admin23432", "email": "upc@example.com"}
USER2 = {"login": "test_user", "password": "user23432",
         "email": "upc2@example.com"}


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
def user2(register_user):
    response = register_user(**USER2)
    return response


@pytest.fixture
def user_logined(user, login_user):
    response = login_user(USER["login"], USER["password"])
    return response

@pytest.fixture
def user_three_history(user, login_user):
    response = login_user(USER["login"], USER["password"])
    response = login_user(USER["login"], USER["password"])
    response = login_user(USER["login"], USER["password"])
    return response

@pytest.fixture
def user2_logined(user, login_user):
    response = login_user(USER["login"], USER["password"])
    return response

@pytest.fixture
def user_two_logined(user_logined, user2_logined):
    return user_logined, user2_logined

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


@pytest.fixture
def password_change(http_post):
    def inner(old_password, new_password):
        endpoint = "password_change"
        payload = {
            "old_password": USER["password"],
            "new_password": "new_valid_password"
        }
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
        ("validlogin", "valid password", HTTPStatus.UNPROCESSABLE_ENTITY,
         False),
        (USER["login"], USER["password"], HTTPStatus.OK, True),
    ],
)
def test_logout(
        refresh_token, token, response_status, success, user_logined,
        logout_user
) -> None:
    if success:
        refresh_token = user_logined.body["data"].get("refresh_token")
        token = user_logined.body["data"].get("access_token")
    response = logout_user(refresh_token, token)
    assert response.status == response_status


@pytest.mark.parametrize(
    "old, new, response_status, success",
    [
        ("1234", "", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("1234", "sdhgxfdbnfhdfhfd", HTTPStatus.UNAUTHORIZED, False),
        (USER["password"], "new_valid_password", HTTPStatus.OK, True),
    ],
)
def test_password_change(
        old, new, response_status, success, user_logined, http_post
) -> None:
    token = user_logined.body["data"].get("access_token")
    endpoint = "password_change"
    payload = {
        "old_password": old,
        "new_password": new
    }
    response = http_post(endpoint, payload, token)
    assert response.status == response_status


@pytest.mark.parametrize(
    "refresh_token, response_status, success",
    [
        ("sdzffdh", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", HTTPStatus.OK, True),
    ],
)
def test_logout_all(
        refresh_token, response_status, success, user_logined,
        http_post
) -> None:
    endpoint = "logout_all"
    user1 = user_logined
    token = user1.body["data"].get("access_token")
    if success:
        refresh_token = user1.body["data"].get("refresh_token")

    payload = {
        "refresh_token": refresh_token,
    }
    response = http_post(endpoint, payload, token)
    assert response.status == response_status
    # response2 = http_post("logout", payload, token)
    # assert response2.status == "response_status"


@pytest.mark.parametrize(
    "token, response_status, success",
    [
        ("sdzffdh", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", HTTPStatus.OK, True),
    ],
)
def test_refresh(
        token, response_status, success, user_logined,
        http_post
) -> None:
    endpoint = "refresh"
    user = user_logined
    if success:
        token = user.body["data"].get("refresh_token")

    response = http_post(endpoint, token=token)
    assert response.status == response_status


@pytest.mark.parametrize(
    "token, response_status, success",
    [
        ("sdzffdh", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", HTTPStatus.OK, True),
    ],
)
def test_login_history(
        token, response_status, success, user_three_history,
        http_get
) -> None:
    endpoint = "user/login_history"
    user = user_three_history
    if success:
        token = user.body["data"].get("access_token")

    response = http_get(endpoint, token=token)
    assert response.status == response_status
    if data := response.body.get("data"):
        assert len(data) == 3