# CLAUDE.md - Credit Risk Platform

> This file is Claude's persistent memory for this project. Read it at the start of every session.

## Project Overview

Migrating a Streamlit credit risk modeling demo to a production-grade monorepo.

**Status**: Phase 1 - Foundation (bootstrapping `shared/` layer)

## Architecture

```
apps/web/     → Next.js 16 (App Router, TypeScript strict) - Production UI
apps/api/     → FastAPI (Python 3.12+, async-first) - Model serving
apps/gradio/  → Gradio (stakeholder demos, HF Spaces)
shared/       → Pydantic schemas + business logic (SINGLE SOURCE OF TRUTH)
notebooks/    → Marimo (.py files only) - Developer exploration
docs/         → RFCs/, ADRs/
```

**UI progression**: Marimo (explore) → Gradio (validate) → Next.js (ship)

## Commands

| Alias | Command | Description |
|-------|---------|-------------|
| `/run` | `uv run pytest && npm test` | Run all tests |
| `/lint` | `uv run ruff check . && npm run lint` | Lint all code |
| `/format` | `uv run ruff format . && npm run format` | Format all code |

## Git Workflow

### Branch Naming

```
feature/   → new functionality (feature/shared-layer-foundation)
fix/       → bug fixes (fix/threshold-edge-case)
refactor/  → code restructuring (refactor/extract-constants)
docs/      → documentation only (docs/update-readme)
chore/     → maintenance (chore/update-deps)
```

### Commit Convention

Use conventional commits with scope:

```
feat(shared): add loan application schema
fix(api): handle empty dataset error
test(shared): add threshold edge cases
docs(rfc): update migration timeline
chore: update dependencies
refactor(api): extract training service
```

### Workflow

1. **Start work:**

   ```bash
   git checkout main && git pull
   git checkout -b feature/[description]
   ```

2. **Commit frequently** — small, atomic commits

3. **Push and PR:**

   ```bash
   git push -u origin feature/[description]
   gh pr create --title "feat(scope): description"
   ```

4. **Merge** — wait for review (don't self-merge)

### Claude Code Git Permissions

Claude can: create branches, commit, push, create PRs
Claude should NOT: merge PRs, force push, rebase shared branches

## Current Phase Tasks

- [x] RFC-001 drafted
- [ ] `shared/schemas/` created with Pydantic models
- [ ] `shared/logic/` created with threshold + evaluation
- [ ] Tests passing with 90%+ coverage
- [ ] `apps/api/` FastAPI endpoints
- [ ] `notebooks/` Marimo apps
- [ ] `apps/web/` Next.js UI

## Conventions

### Python (apps/api/, shared/, notebooks/)

- Python 3.12+
- Pydantic v2 (not v1 syntax)
- `uv` for dependency management
- Ruff for linting and formatting
- pytest for testing
- Type hints required on all functions
- Docstrings required on all public functions/classes

### TypeScript (apps/web/)

- TypeScript strict mode
- Biome for linting and formatting
- npm for dependency management
- Interfaces must sync with Pydantic schemas in `shared/`

### Notebooks

- Marimo only (no Jupyter)
- Store as `.py` files (not `.ipynb`)
- Import from `shared/` for schemas and logic
- Deployable to Molab

## Key Files

| File | Purpose |
|------|---------|
| `docs/RFCs/RFC-001-*.md` | Architecture decision |
| `shared/schemas/loan.py` | Core data models |
| `shared/logic/threshold.py` | Youden's J implementation |
| `data/raw/cr_loan_w2.csv` | Training dataset |

## Schema Sync Protocol

When Pydantic schemas in `shared/` change:

1. Update the schema
2. Run `uv run pytest tests/shared/`
3. Regenerate TS interfaces (TBD: manual or codegen)
4. Update `apps/web/` components

## Do NOT

- Add pandas to `shared/` (keep logic layer pure numpy/sklearn)
- Use Jupyter notebooks (Marimo only)
- Skip type hints or docstrings
- Commit without running `/run`

## Skills

Claude Code skills are in `.claude_skills/` (gitignored). Reference them for domain-specific patterns.

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `rfc` | Write RFC documents | "Write an RFC for...", "Propose..." |

To use a skill, Claude reads the SKILL.md and follows its structure. Skills are local to developer machines and not committed to git.

### Adding Skills

Place skill folders in `.claude_skills/`:

```
.claude_skills/
├── rfc/
│   ├── SKILL.md
│   └── references/
│       └── rfc-template.md
└── [other-skills]/
```

Each skill has a SKILL.md with frontmatter (name, description) and instructions.
