import pytest
from elasticsearch import AsyncElasticsearch, Elasticsearch
from functional.settings import test_settings


@pytest.fixture(scope="session")
async def es_async_client():
    client = AsyncElasticsearch(
        hosts=test_settings.elastic_dsn, ignore_status=[400, 404]
    )
    yield client
    await client.close()


@pytest.fixture(scope="session")
def es_client():
    client = Elasticsearch(
        hosts=test_settings.elastic_dsn, ignore_status=[400, 404]
    )
    yield client
    client.close()


def _restore_indexes(make_es_repo, es_client):
    index_body = {"indices": ",".join(test_settings.index_names)}

    for index in es_client.indices.get(index="*"):
        if index in test_settings.index_names:
            es_client.indices.close(index=index)

    es_client.snapshot.restore(
        repository=test_settings.repo_name,
        snapshot=test_settings.snapshot_name,
        body=index_body,
    )

    for index in es_client.indices.get(index="*"):
        if index in test_settings.index_names:
            es_client.indices.open(index=index)


@pytest.fixture(scope="session", autouse=True)
def set_up_es_indexes_once(make_es_repo, es_client):
    _restore_indexes(make_es_repo, es_client)
    return "ok"


@pytest.fixture
def restore_indexes_after(make_es_repo, es_client):
    yield
    _restore_indexes(make_es_repo, es_client)


@pytest.fixture(scope="session")
def make_es_repo(es_client):
    snapshot_body = {
        "type": "fs",
        "settings": {
            "location": "/tmp/test_repo",
            "max_restore_bytes_per_sec": "40mb",
            "readonly": "false",
            "compress": "true",
            "max_snapshot_bytes_per_sec": "40mb",
        },
    }
    es_client.snapshot.create_repository(
        repository=test_settings.repo_name, body=snapshot_body
    )


@pytest.fixture
def make_indexes_snapshot(make_es_repo, es_client):
    """
    Is called manually when you want to create a new snapshot to use in tests.
    You might want to use it if you've changed index structure or contents.

    1. Start test ES with `environment: - 'path.repo=/tmp/test_repo/'`
    2. Make indexes and fill them (e.g. with ETL)
    3. Make repo and snapshot with this function
    4. `make elasticsearch` and go into container
    5. `cd /tmp``zip -r indexes_snapshot.zip test_repo` exit container shell
    6. copy file to host `docker cp elasticsearch:/tmp/indexes_snapshot.zip .`, move it to /testdata in repo
    All this in an attempt to isolate test data and not depend on ETL process for it.
    There's gotta be a better way...

    TODO: make `make` command for setting this up
    :param make_es_repo:
    :param es_client:
    :return:
    """

    index_body = {"indices": ",".join(test_settings.index_names)}
    es_client.snapshot.create(
        repository=test_settings.repo_name,
        snapshot=test_settings.snapshot_name,
        body=index_body,
    )
