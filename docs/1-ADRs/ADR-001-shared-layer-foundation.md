# ADR-001: Shared Layer Foundation

| Field | Value |
|-------|-------|
| Status | Accepted |
| Author | Paul / Claude |
| Date | 2025-01-31 |
| RFC | RFC-001 |
| PR | [link to merged PR] |

## Context

Migrating from a monolithic Streamlit app required establishing a single source of truth for schemas and business logic before building API or UI layers.

## Decision

Implemented `shared/` package with:

### Schemas (`shared/schemas/`)

| Schema | Purpose |
|--------|---------|
| `LoanApplication` | Single loan record with validated fields |
| `LoanDataset` | Collection of loans with labels |
| `TrainingConfig` | Model hyperparameters and settings |
| `TrainingResult` | Training output with metrics |
| `ModelMetrics` | Accuracy, precision, recall, F1, ROC-AUC |
| `ThresholdResult` | Youden's J optimization output |
| `PredictionRequest` | Inference input |
| `PredictionResponse` | Inference output |
| `AuditEvent` | Immutable event log entry |

### Logic (`shared/logic/`)

| Module | Functions |
|--------|-----------|
| `threshold.py` | `find_optimal_threshold()` — Youden's J statistic |
| `evaluation.py` | ROC curve, AUC, calibration curve, confusion matrix |
| `preprocessing.py` | Categorical encoding, undersampling |

### Constants (`shared/constants.py`)

- `NUMERIC_FEATURES`, `CATEGORICAL_FEATURES`
- `TARGET_COLUMN`, `DEFAULT_TEST_SIZE`, `DEFAULT_RANDOM_STATE`
- Model type literals, validation bounds

## Constraints Applied

- **No pandas in shared/** — pure numpy/sklearn for logic layer
- **Pydantic v2 only** — `field_validator` not `validator`
- **Frozen models** — immutable where appropriate (AuditEvent)
- **Type hints required** — all functions annotated
- **Docstrings required** — all public APIs documented

## Verification

- 82 unit tests, 100% pass rate
- Ruff linting clean
- Coverage target met

## Consequences

- All downstream layers (API, notebooks, web) import from `shared/`
- TypeScript interfaces in `apps/web/` must sync with these schemas
- Adding new fields requires updating schemas first, then consumers
