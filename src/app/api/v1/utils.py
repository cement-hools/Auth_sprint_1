from functools import wraps
from http import HTTPStatus
from typing import Callable, Type

from app.api.v1.schemas import BaseResponse
from flask import request
from pydantic import BaseModel, ValidationError
from settings import logger


def body_validator(
    body: Type[BaseModel] = None,
    validation_error_status_code: int = HTTPStatus.UNPROCESSABLE_ENTITY,
):
    def decorate(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            clean_body = None

            try:
                if body:
                    clean_body = body(**request.get_json())

            except ValidationError as err:
                logger.error("{}: {}", err.__class__.__name__, err)
                error_message = err.errors()
                return (
                    BaseResponse(success=False, error=error_message).dict()
                ), validation_error_status_code

            request.clean_body = clean_body

            res = func(*args, **kwargs)

            return res

        return wrapper

    return decorate
