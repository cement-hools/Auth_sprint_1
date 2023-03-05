import os
import re
import sys
import logging
from loguru import logger as loguru_logger


def obfuscate_message(message: str):
    """Obfuscate sensitive information."""
    result = re.sub(
        r"password[\"\']: '.*?'", "password': [obfuscated]", message
    )
    result = re.sub(
        r"token[\"\']: [\"\'].*?[\"\']", 'token": [obfuscated]', result
    )
    return result


def formatter(record):
    record["extra"]["obfuscated_message"] = obfuscate_message(
        record["message"]
    )
    return "[{level}] {time} | {extra[obfuscated_message]}\n{exception}"


logger = loguru_logger
logger.remove()
logger.add(sys.stderr, format=formatter, level="DEBUG")


# create a custom handler
class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
    """
    When running with gunicorn the log handlers get suppressed instead of
    passed along to the container manager. This forces the gunicorn handlers
    to be used throughout the project.
    """

    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger("gunicorn.error").handle(record)

    logger.remove()
    logger.add(PropagateHandler(), format=formatter, level="DEBUG")
    logger.warning("Logging with Gunicorn")
