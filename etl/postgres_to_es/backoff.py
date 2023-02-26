import logging
import sqlite3
from functools import wraps
from time import sleep
from typing import Any

import psycopg2

loggerb = logging.getLogger(__name__)


def my_backoff(
    start_sleep_time=0.1, factor=2, border_sleep_time=10, logger=loggerb
) -> Any:
    """Функция для повторного выполнения функции через некоторое время, если
    возникла ошибка.
    Args:
        start_sleep_time (float, optional): начальное время повтора.
        factor (int, optional): количество увеличения времени ожидания.
        border_sleep_time (int, optional): граничное время ожидания.
        logger (logging): информатор
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(e)
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    else:
                        sleep_time = min(
                            sleep_time * factor, border_sleep_time
                        )
                    sleep(sleep_time)

        return inner

    return func_wrapper


def db_error_handler(func):
    def inner_function(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except sqlite3.Error as err:
            loggerb.error(f'Ошибка SQLite: {" ".join(err.args)}')
        except psycopg2.Error as err:
            loggerb.error(f"Postgres error: {err.pgcode}")
            loggerb.error(err)
        return result

    return inner_function
