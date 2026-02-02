"""Structured logging configuration using structlog."""

import logging
from pathlib import Path

import structlog


def setup_logging(
    log_level: str = "INFO", audit_path: str = "logs/audit.jsonl"
) -> None:
    """Configure structured logging with structlog.

    Sets up JSON-formatted structured logging and an audit log file handler.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        audit_path: File path for the JSONL audit log.
    """
    Path(audit_path).parent.mkdir(parents=True, exist_ok=True)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set up audit file handler
    audit_handler = logging.FileHandler(audit_path)
    audit_handler.setLevel(logging.INFO)

    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
