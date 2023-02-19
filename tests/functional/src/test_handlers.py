import asyncio
import uuid
from http import HTTPStatus

import pytest
from sqlalchemy import MetaData, create_engine, text, select
from sqlalchemy.dialects.postgresql import insert

from tests.functional.fixtures.async_http import HTTPResponse
from tests.functional.settings import test_settings

USER = {"login": "admin", "password": "admin23432", "email": "upc@example.com"}
USER2 = {"login": "testuser", "password": "user23432",
         "email": "upc2@example.com"}
ROLE_ADMIN = {"name": "admin", "description": "admin role"}
ROLE_USER = {"name": "user", "description": "user role"}


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
def roles_admin():
    engine = create_engine(test_settings.postgres_dsn)

    with engine.begin() as conn:
        uid = uuid.uuid4()
        name = ROLE_ADMIN["name"]
        description = ROLE_ADMIN["description"]
        query = text(
            "insert into roles (id, name, description) "
            f"values ('{uid}', '{name}', '{description}');"
        )
        conn.execute(query)

        return uid


@pytest.fixture
def roles_user():
    engine = create_engine(test_settings.postgres_dsn)

    with engine.begin() as conn:
        uid = uuid.uuid4()
        name = ROLE_USER["name"]
        description = ROLE_USER["description"]
        query = text(
            "insert into roles (id, name, description) "
            f"values ('{uid}', '{name}', '{description}');"
        )
        conn.execute(query)
        return uid


@pytest.fixture
def roles(roles_admin, roles_user):
    return roles_admin, roles_user


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
    return response.body["data"]


@pytest.fixture
def user_logined(user, login_user):
    response = login_user(USER["login"], USER["password"])
    return response


@pytest.fixture
def user_logined_admin_user_role(user_logined, roles):
    engine = create_engine(test_settings.postgres_dsn)
    admin_role_id = roles[0]

    with engine.begin() as conn:
        user_query = text("select id from users where login = 'admin';")
        user = conn.execute(user_query).fetchone()
        user_id = user[0]
        uid = uuid.uuid4()
        query = text(
            "insert into user_role (id, user_id, role_id) "
            f"values ('{uid}', '{user_id}', '{admin_role_id}');"
        )
        res = conn.execute(query)
    return user_logined, admin_role_id


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
    def inner(old_password, new_password, token):
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


@pytest.mark.parametrize(
    "token, response_status, success",
    [
        ("sdzffdh", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", HTTPStatus.OK, True),
    ],
)
def test_user_roles_list(
        token, response_status, success, user_logined_admin_user_role,
        http_get
) -> None:
    endpoint = "user/roles"
    user, role_id = user_logined_admin_user_role
    if success:
        token = user.body["data"].get("access_token")

    response = http_get(endpoint, token=token)
    assert response.status == response_status
    if success:
        data = response.body["data"]
        assert len(data) == 1
        assert data[0]["id"] == str(role_id)


@pytest.mark.parametrize(
    "token, response_status, success",
    [
        ("sdzffdh", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", HTTPStatus.OK, True),
    ],
)
def test_all_roles(
        token, response_status, success, user_logined_admin_user_role,
        http_get
) -> None:
    endpoint = "roles"
    user, role_id = user_logined_admin_user_role
    if success:
        token = user.body["data"].get("access_token")

    response = http_get(endpoint, token=token)
    assert response.status == response_status
    if success:
        data = response.body["data"]
        assert len(data) == 2


@pytest.mark.parametrize(
    "token, response_status, success",
    [
        ("sdzffdh", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", HTTPStatus.OK, True),
    ],
)
def test_create_role(
        token, response_status, success, user_logined_admin_user_role,
        http_post
) -> None:
    endpoint = "roles"
    user = user_logined_admin_user_role[0]
    if success:
        token = user.body["data"].get("access_token")
    payload = {
        "name": "test_role", "description": "test_role_description"
    }
    response = http_post(endpoint, payload, token=token)
    assert response.status == response_status
    if success:
        data = response.body["data"]
        assert data["name"] == payload["name"]


@pytest.mark.parametrize(
    "token, response_status, success",
    [
        ("sdzffdh", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", HTTPStatus.OK, True),
    ],
)
def test_detail_role(
        token, response_status, success, user_logined_admin_user_role,
        http_get
) -> None:
    user, role_id = user_logined_admin_user_role
    endpoint = f"roles/{role_id}"
    if success:
        token = user.body["data"].get("access_token")

    response = http_get(endpoint, token=token)
    assert response.status == response_status
    if success:
        data = response.body["data"]
        assert data["name"] == ROLE_ADMIN["name"]


@pytest.mark.parametrize(
    "token, response_status, success",
    [
        ("sdzffdh", HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", HTTPStatus.OK, True),
    ],
)
def test_edit_role(
        token, response_status, success, user_logined_admin_user_role,
        http_put
) -> None:
    user, role_id = user_logined_admin_user_role
    endpoint = f"roles/{role_id}"
    if success:
        token = user.body["data"].get("access_token")
    payload = {
        "name": "test_role", "description": "test_role_description"
    }
    response = http_put(endpoint, payload, token=token)
    assert response.status == response_status
    if success:
        data = response.body["data"]
        assert data["name"] == payload["name"]


@pytest.mark.parametrize(
    "token, role_id, response_status, success",
    [
        ("sdzffdh", uuid.uuid4(), HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("", uuid.uuid4(), HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", "", HTTPStatus.OK, True),
    ],
)
def test_delete_role(
        token, role_id, response_status, success, user_logined_admin_user_role,
        http_delete
) -> None:
    user, role_id_exist = user_logined_admin_user_role
    endpoint = f"roles/{role_id}"
    if success:
        token = user.body["data"].get("access_token")
        endpoint = f"roles/{role_id_exist}"

    response = http_delete(endpoint, token=token)
    assert response.status == response_status



@pytest.mark.parametrize(
    "token, role_id, response_status, success",
    [
        ("sdzffdh", uuid.uuid4(), HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("", uuid.uuid4(), HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", "", HTTPStatus.OK, True),
    ],
)
def test_delete_role(
        token, role_id, response_status, success, user_logined_admin_user_role,
        http_delete
) -> None:
    user, role_id_exist = user_logined_admin_user_role
    endpoint = f"roles/{role_id}"
    if success:
        token = user.body["data"].get("access_token")
        endpoint = f"roles/{role_id_exist}"

    response = http_delete(endpoint, token=token)
    assert response.status == response_status


@pytest.mark.parametrize(
    "token, role_id, response_status, success",
    [
        ("sdzffdh", uuid.uuid4(), HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("", uuid.uuid4(), HTTPStatus.UNPROCESSABLE_ENTITY, False),
        ("valid", "", HTTPStatus.OK, True),
    ],
)
def test_add_role_to_user(
        token, role_id, response_status, success, user_logined_admin_user_role,
        http_post, user2
) -> None:
    user, admin_role_id = user_logined_admin_user_role
    endpoint = f"roles/{admin_role_id}/add_user"
    if success:
        token = user.body["data"].get("access_token")
    payload = {"user_id": user2['id']}
    response = http_post(endpoint, payload, token)
    assert response.status == response_status
    assert response.body.get("success", False) == success