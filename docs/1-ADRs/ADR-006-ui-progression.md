# ADR-006: UI Progression (Marimo → Gradio → Next.js)

| Field | Value |
|-------|-------|
| Status | Accepted |
| Author | Paul / Claude |
| Date | 2026-02-01 |
| PR | [#21](https://github.com/pkiage/tool-credit-risk-modelling/pull/21) |

## Context

Needed multiple UI layers for different audiences and iteration speeds.

## Decision

Three-tier UI progression:

| Layer | Audience | Speed | Polish |
|-------|----------|-------|--------|
| Marimo | Developers | Fastest | Low |
| Gradio | Stakeholders | Fast | Medium |
| Next.js | End users | Slower | High |

- Marimo for exploration and prototyping
- Gradio for quick stakeholder demos (HF Spaces)
- Next.js for production UI

## Consequences

- Three UI codebases to maintain
- Can validate UX in Gradio before investing in Next.js
- Stakeholders get early access via Gradio
- All UIs call `apps/api/` — no logic duplication
