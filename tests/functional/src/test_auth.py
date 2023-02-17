from http import HTTPStatus

import pytest
from sqlalchemy import MetaData, create_engine, text

from tests.functional.fixtures.async_http import HTTPResponse
from tests.functional.settings import test_settings


@pytest.fixture(scope="session", autouse=True)
def db_delete_everything(request):
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
        ("validlogin", "valid@ema.il", "valid password", HTTPStatus.OK, True),
    ],
)
async def test_registration(
    login, email, password, response_status, success, register_user
) -> None:
    response = await register_user(login, email, password)
    assert response.status == response_status
    assert response.body.get("success") == success
