from typing import Type

from pydantic import BaseModel, ValidationError
from app.settings.logging import logger

from flask import abort, request


def get_body(request_model: Type[BaseModel]):
    """
    Получить body запроса и провалидировать,
    что body соответствует схеме.
    """
    try:
        body = request_model.parse_obj(request.get_json())
    except ValidationError as err:
        logger.error("{}: {}", err.__class__.__name__, err)
        error_message = err.errors()
        abort(422, description=error_message)
    else:
        return body
