import inspect
import logging
import sys

from loguru import logger

from vkusvill_green_labels.core.settings import settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=settings.log_level)

    if settings.log_level == "DEBUG":
        # Log all SQL queries
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    for log in [
        "aiogram",
        "httpcore",
        "tzlocal",
        "httpx",
        "aiogram.dispatcher",
        "aiogram.event",
        "apscheduler",
    ]:
        # Set the log level to INFO even when debug is enabled.
        logging.getLogger(log).setLevel(logging.INFO)
