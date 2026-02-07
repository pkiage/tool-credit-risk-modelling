# ADR-005: Model Persistence Strategy

| Field | Value |
|-------|-------|
| Status | Accepted |
| Author | Paul / Claude |
| Date | 2026-02-02 |
| RFC | [RFC-006](../0-RFCs/RFC-006-auth-polish.md) |
| PR | [#19](https://github.com/pkiage/tool-credit-risk-modelling/pull/19) |

## Context

Trained models were only stored in memory and lost on API restart. We needed a persistence strategy that preserves models across restarts while keeping the architecture simple.

## Decision

Use filesystem-based persistence with joblib serialization.

**Implementation:**
- Models saved as `.joblib` files with companion `.json` metadata
- Default path: `artifacts/` (configurable via `CREDIT_RISK_MODEL_ARTIFACTS_PATH`)
- `PersistentModelStore` class handles save/load/list/delete
- In-memory store remains for session-scoped models
- Persist endpoint (`POST /models/{id}/persist`) writes to disk on demand

**Why joblib over pickle:**
- Optimized for numpy arrays and sklearn models
- Better compression for large objects
- Standard in the sklearn ecosystem

## Alternatives Considered

- **MLflow** — Full model registry but heavy dependency for current scope
- **S3/cloud storage** — Requires cloud credentials; documented as upgrade path
- **Database (BLOB)** — Adds database dependency, poor for large binary objects
- **ONNX export** — Good for inference but loses sklearn API compatibility

## Consequences

- Models persist across API restarts when explicitly saved
- Artifact directory must be backed up in production
- S3 extension documented in RFC-006 for future production use
- No model versioning (model_id is the version key)
