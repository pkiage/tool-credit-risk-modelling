"""Pydantic schemas for credit risk modeling."""

from shared.schemas.audit import (
    AuditEvent,
    PredictionAuditEvent,
    ThresholdChangeAuditEvent,
    TrainingAuditEvent,
)
from shared.schemas.loan import LoanApplication, LoanDataset
from shared.schemas.metrics import (
    CalibrationCurve,
    ConfusionMatrix,
    ModelMetrics,
    ROCCurveData,
    ThresholdResult,
)
from shared.schemas.model import ModelMetadata, PersistResponse
from shared.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionResult,
)
from shared.schemas.training import TrainingConfig, TrainingResult

__all__ = [
    # Audit
    "AuditEvent",
    "PredictionAuditEvent",
    "ThresholdChangeAuditEvent",
    "TrainingAuditEvent",
    # Loan
    "LoanApplication",
    "LoanDataset",
    # Metrics
    "CalibrationCurve",
    "ConfusionMatrix",
    "ModelMetrics",
    "ROCCurveData",
    "ThresholdResult",
    # Model
    "ModelMetadata",
    "PersistResponse",
    # Prediction
    "PredictionRequest",
    "PredictionResponse",
    "PredictionResult",
    # Training
    "TrainingConfig",
    "TrainingResult",
]
