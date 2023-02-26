import datetime
import logging
import sys
import time

import psycopg2
from backoff import my_backoff
from db_query import load_film_id
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from ps_to_es import (
    es_create_genre_index,
    es_create_person_index,
    es_create_show_index,
    generate_actions,
    generate_genre_actions,
    generate_person_actions,
)
from psycopg2.extras import RealDictCursor
from settings import settings
from sqlite_functions import get_lsl_from_sqlite, save_to_sqlite

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@my_backoff()
def etl_cycle():
    """Класс запуска ETL-цикла"""
    es_client = Elasticsearch(hosts=settings.elastic_dsn)
    pg_connection = psycopg2.connect(
        dsn=settings.postgres_dsn, cursor_factory=RealDictCursor
    )
    try:
        while True:
            main(
                pg_connection=pg_connection,
                es_client=es_client,
                sqlite_db_path=settings.sqlite_db_path,
                frequency=settings.time_loop,
            )
    finally:
        es_client.transport.close()
        pg_connection.close()
        return logger.info("Разрыв соединения Elasticsearch и Postgres")


@my_backoff()
def main(
    pg_connection: psycopg2.extensions.connection,
    es_client: Elasticsearch,
    sqlite_db_path: str,
    frequency: int,
):
    """
    Метод переноса измененных данных из PG в индекс Elasticsearch

    pg_connection: подключение
    es_client: ES-клиент
    sqlite_db_path: путь до БД
    """
    logger.info("Начало нового цикла")
    last_successful_load = datetime.datetime.fromisoformat(
        get_lsl_from_sqlite(sqlite_db_path)
    ).replace(tzinfo=datetime.timezone.utc)
    logger.info(f"Последняя загрузка: {last_successful_load}")

    time_since = (
        datetime.datetime.now(datetime.timezone.utc) - last_successful_load
    ).total_seconds()
    if time_since < frequency:
        logger.info(
            f"Последний пул был {frequency} секунд назад. Скоро начнется новый"
        )
        time.sleep(frequency - time_since)

    start_time = datetime.datetime.now(datetime.timezone.utc)
    logger.info("Начало загрузки")
    etl_successful = False

    save_to_sqlite(start_time, etl_successful, sqlite_db_path)

    logger.info("Перенос данных в Postgres")
    with pg_connection:
        pg_cursor = pg_connection.cursor()
        pg_cursor.execute(load_film_id)
        logger.debug(pg_cursor.fetchone())
        pg_cursor = pg_connection.cursor()
        # Размер состояния, которое будет передано в Elastic
        pg_cursor.itersize = settings.bulk_size

        es_create_show_index(es_client)
        es_create_genre_index(es_client)
        es_create_person_index(es_client)

        create_indexes_defs = {
            "shows": generate_actions(pg_cursor, last_successful_load),
            "persons": generate_person_actions(
                pg_cursor, last_successful_load
            ),
            "genres": generate_genre_actions(pg_cursor, last_successful_load),
        }

        for index in settings.indexes:
            logger.info(f"Заполнение индекса {index} данными")
            filling_indexes_with_data(
                client=es_client,
                index=index,
                create_indexes_defs=create_indexes_defs,
            )

        etl_successful = True

    save_to_sqlite(start_time, etl_successful, sqlite_db_path)
    if settings.only_one_etl_cycle and etl_successful:
        logger.info("Only one ETL cycle needed, exiting ETL.")
        sys.exit(0)


def filling_indexes_with_data(client, index, create_indexes_defs):
    i = 0
    streaming_blk_index = streaming_bulk(
        client=client,
        index=index,
        actions=create_indexes_defs[index],
        max_retries=100,
        initial_backoff=0.1,
        max_backoff=10,
    )
    for ok, response in streaming_blk_index:
        if not ok:
            return logger.error(f"Ошибка при передаче данных {index}")
        logger.debug(response)
        i += 1
    etl_successful = True
    if etl_successful:
        return logger.info(f"Перенос завершен успешно. Проведена {i} операция")
    return logger.info(f"Индекс {index} создан, но перенесены не все данные")


if __name__ == "__main__":
    etl_cycle()
