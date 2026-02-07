# ADR-008: Monorepo Structure

| Field | Value |
|-------|-------|
| Status | Accepted |
| Author | Paul / Claude |
| Date | 2026-02-02 |
| PR | [#21](https://github.com/pkiage/tool-credit-risk-modelling/pull/21) |

## Context

Migrating from monolithic Streamlit app. Needed structure for multiple apps sharing code.

## Decision

Monorepo with clear separation:

```
apps/api/     → FastAPI backend
apps/web/     → Next.js frontend
apps/gradio/  → Gradio demo
shared/       → Pydantic schemas + logic (single source of truth)
notebooks/    → Marimo notebooks
```

- `uv` workspaces for Python
- `npm` workspaces for Node (if needed)
- `shared/` importable by all Python layers

## Consequences

- Single repo, single PR for cross-cutting changes
- `shared/` must not have heavy dependencies
- TypeScript types manually synced with Pydantic
- Clear ownership per directory
