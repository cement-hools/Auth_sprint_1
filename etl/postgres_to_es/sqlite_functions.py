import datetime
import logging
import sqlite3
from contextlib import contextmanager

from backoff import db_error_handler
from db_query import (create_a_table, delete_old_states,
                      insert_last_successful_load_time, last_success_load_time)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@contextmanager
def sqlite_connection_context(db_path: str):
    connection = sqlite3.connect(db_path)
    yield connection
    connection.commit()
    connection.close()


@db_error_handler
def get_lsl_from_sqlite(sqlite_db_path):
    """Метод получения последнего успешного запроса"""
    with sqlite_connection_context(sqlite_db_path) as _connection:
        sqlite_cursor = _connection.cursor()
        sqlite_cursor.execute(create_a_table)
        sqlite_cursor.execute(delete_old_states)
        last_successful_load = sqlite_cursor.execute(last_success_load_time).fetchone()
        if last_successful_load is None:
            last_successful_load = [
                datetime.datetime(1970, 1, 1).isoformat(timespec='seconds')
            ]
            logger.debug('LSL не найден')
    return last_successful_load[0]


# Декоратор логирования ошибок при работе БД
@db_error_handler
def save_to_sqlite(start_time, etl_successful, sqlite_db_path) -> None:
    """Метод сохранения изменений в SQLite"""
    with sqlite_connection_context(sqlite_db_path) as _connection:
        sqlite_cursor = _connection.cursor()
        time = datetime.datetime.now().isoformat(timespec='seconds')
        sqlite_cursor.execute(
            insert_last_successful_load_time.format(
                start_time.isoformat(timespec='seconds'),
                etl_successful, time
            ),
        )
