from app.settings.logging import logger

from flask import request


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
