"""Structured logger setup using structlog."""

import logging
from typing import Any

import structlog


def configure_logging(debug: bool = False) -> None:
    """Configure structlog with rich console output."""
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    shared_processors: list[Any] = [
        timestamper,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[*shared_processors, structlog.dev.ConsoleRenderer(colors=True)],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)


