# ADR-007: Chart Library (Recharts)

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-02-02 |
| RFC | RFC-005 |

## Context

Needed charting for ROC curves, calibration plots, confusion matrices in Next.js UI.

Options considered:
- Recharts (React-native, good TS support)
- Plotly.js (powerful, used in notebooks)
- Nivo (D3-based, declarative)
- Chart.js (lightweight)

## Decision

Chose Recharts for Next.js because:
- React-native (not a wrapper)
- Good TypeScript support
- Simpler API than Plotly
- Sufficient for our chart types

Kept Plotly in notebooks/Gradio for consistency with Python ecosystem.

## Consequences

- Next.js uses Recharts
- Notebooks/Gradio use Plotly
- Chart styling may differ slightly between layers
- Team needs to know two charting libraries
