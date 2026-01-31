"""Audit event logging service."""

import json
import logging

from shared.schemas.audit import AuditEvent

# Configure audit logger
logger = logging.getLogger("audit")


def emit_event(event: AuditEvent) -> None:
    """Emit an audit event to structured logging.

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
    # Log event as structured JSON
    logger.info(json.dumps(event.model_dump(), default=str))
