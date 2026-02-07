# ADR-002: Pydantic as Contract Layer

| Field | Value |
|-------|-------|
| Status | Accepted |
| Author | Paul / Claude |
| Date | 2026-02-02 |
| RFC | [RFC-001](../0-RFCs/RFC-001-CreditRiskPlatformArchitecture.md) |
| PR | [#19](https://github.com/pkiage/tool-credit-risk-modelling/pull/19) |

## Context

The platform spans Python (API, notebooks, Gradio) and TypeScript (Next.js). We needed a single source of truth for data contracts that could be validated at runtime and generate TypeScript interfaces.

## Decision

Use Pydantic v2 models in `shared/schemas/` as the canonical contract layer.

**Why Pydantic v2:**
- Runtime validation with detailed error messages
- JSON Schema generation for TypeScript codegen via `datamodel-code-generator`
- Frozen models for immutability where needed (e.g., `AuditEvent`)
- `field_validator` for cross-field validation
- Native support in FastAPI for request/response serialization

## Alternatives Considered

- **dataclasses** — No runtime validation, no JSON Schema generation
- **attrs** — Less FastAPI integration, smaller ecosystem
- **Protocol/TypedDict** — No runtime validation

## Consequences

- All API request/response types are Pydantic models
- TypeScript interfaces in `apps/web/lib/types.ts` must stay in sync
- Schema changes require updating all consumers (API, Gradio, web)
- `shared/` must not import from `apps/` (dependency inversion)
