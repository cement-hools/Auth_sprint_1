from typing import Type

from flask import abort, request
from pydantic import BaseModel, ValidationError

from settings import logger


def get_body(request_model: Type[BaseModel]):
    """Получить body запроса и провалидировать, что body соответствует схеме."""
    try:
        body = request_model.parse_obj(request.get_json())
    except ValidationError as err:
        logger.error("{}: {}", err.__class__.__name__, err)
        error_message = err.errors()
        abort(422, description=error_message)
    else:
        return body


def before_request_log():
    logger.info("{}: {}", request.method, request.path)
    logger.debug("{}", request.args)
    if (
        request.content_type == "application/json"
        and int(request.headers.get("Content-Length")) > 0
    ):
        logger.debug("{}", request.get_json())


def after_request_log(response):
    logger.debug(
        "Response for {} {}: {}",
        request.method,
        request.path,
        response.get_json(),
    )
    return response
