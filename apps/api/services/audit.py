"""Audit event logging service using structlog."""

import json
import logging

import structlog

from shared.schemas.audit import AuditEvent

# Structured logger for console/JSON output
struct_logger = structlog.get_logger("audit")
# Stdlib logger for the audit file handler (configured in logging_config)
file_logger = logging.getLogger("audit")


def emit_event(event: AuditEvent) -> None:
    """Emit an audit event to structured logging and the audit log file.

    Args:
        event: Audit event to log.

    Example:
        >>> from shared.schemas.audit import TrainingAuditEvent
        >>> event = TrainingAuditEvent(
        ...     event_id="evt_123",
        ...     model_id="model_456",
        ...     model_type="logistic_regression",
        ...     training_config={"test_size": 0.2},
        ...     dataset_size=1000,
        ...     test_accuracy=0.85
        ... )
        >>> emit_event(event)
    """
    event_data = event.model_dump()

    # Structured log via structlog
    struct_logger.info(
        event.event_type,
        event_id=event.event_id,
        model_id=event.model_id,
        user_id=event.user_id,
    )

    # Audit file log as JSON line
    file_logger.info(json.dumps(event_data, default=str))
