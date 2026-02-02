# ADR-003: Marimo over Jupyter

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-02-02 |
| RFC | RFC-003 |

## Context

Developer exploration notebooks are part of the workflow. We needed a notebook format that works well with git, supports Python imports from `shared/`, and can be deployed.

## Decision

Use Marimo notebooks stored as `.py` files instead of Jupyter `.ipynb` files.

**Why Marimo:**
- Stored as plain `.py` files — clean git diffs, no JSON merge conflicts
- Reactive execution model — cells automatically re-run when dependencies change
- Can import from `shared/` like any Python module
- Deployable to Molab for sharing
- No hidden state issues (a common Jupyter pitfall)

## Alternatives Considered

- **Jupyter** — JSON format causes merge conflicts, hidden state bugs, harder to import from shared packages
- **Quarto** — More suited for publishing, not interactive exploration
- **Plain scripts** — No interactivity or visualization

## Consequences

- All notebooks are `.py` files in `notebooks/`
- No `.ipynb` files in the repository
- Developers need `marimo` installed (`uv run marimo edit notebook.py`)
- Ruff linting applies to notebook files (with relaxed naming rules)
