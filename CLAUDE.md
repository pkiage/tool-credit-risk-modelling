# CLAUDE.md - Credit Risk Platform

> This file is Claude's persistent memory for this project. Read it at the start of every session.

## Project Overview

Migrating a Streamlit credit risk modeling demo to a production-grade monorepo.

**Status**: Phase 7 (cleanup & hardening). All layers implemented: `shared/`, `apps/api/`, `notebooks/`, `apps/gradio/`, `apps/web/`.

## Architecture

```text
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

```text
feature/   → new functionality (feature/shared-layer-foundation)
fix/       → bug fixes (fix/threshold-edge-case)
refactor/  → code restructuring (refactor/extract-constants)
docs/      → documentation only (docs/update-readme)
chore/     → maintenance (chore/update-deps)
```

### Commit Convention

Use conventional commits with scope:

```text
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

5. **After merge — CRITICAL:**

   ```bash
   git checkout main
   git pull origin main
   ```

   Your local main is now up-to-date with merged changes.

### Branch Hygiene

**IMPORTANT: Avoid losing work**

| Rule | Why |
|------|-----|
| Always push before switching branches | Unpushed commits can be lost |
| Always PR before deleting branch | No PR = no record of changes |
| Always pull main after merge | Local main won't have merged code otherwise |
| Never work directly on main | Always use feature branches |

**After PR is merged:**

```bash
# Update local main
git checkout main
git pull origin main

# Delete local feature branch (optional, keeps things clean)
git branch -d feature/[old-branch]
```

**If you downloaded files to wrong branch:**

```bash
# Before doing anything else, commit and push
git add .
git commit -m "wip: save work before branch switch"
git push origin [current-branch]

# Now safe to switch
git checkout main
git pull
```

**Recovering lost work:**

```bash
# If branch was deleted but commits exist
git reflog  # Find the commit hash
git checkout -b recovery-branch [commit-hash]
```

### Claude Code Git Permissions

Claude can: create branches, commit, push, create PRs
Claude should NOT: merge PRs, force push, rebase shared branches

### Pre-Flight Checklist (before starting any task)

```bash
# 1. Make sure you're on main and up-to-date
git checkout main
git pull origin main

# 2. Verify clean state
git status  # Should show "nothing to commit, working tree clean"

# 3. Create feature branch
git checkout -b feature/[description]
```

If `git status` shows uncommitted changes, either commit them or stash:

```bash
git stash  # Temporarily save changes
# ... do your work ...
git stash pop  # Restore changes later
```

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
| `docs/0-RFCs/RFC-001-*.md` | Platform architecture |
| `docs/0-RFCs/RFC-002-*.md` | API layer design |
| `docs/0-RFCs/RFC-006-*.md` | Auth & security |
| `docs/1-ADRs/` | Architecture decision records (ADR-001 through ADR-008) |
| `shared/schemas/loan.py` | Core data models |
| `shared/logic/threshold.py` | Youden's J implementation |
| `data/processed/cr_loan_w2.csv` | Training dataset (one-hot encoded) |

## Schema Sync Protocol

When Pydantic schemas in `shared/` change:

1. Update the schema
2. Run `uv run pytest tests/shared/`
3. Regenerate TS interfaces via `datamodel-code-generator` (see RFC-001 Q4)
4. Update `apps/web/` components
5. Verify `apps/gradio/` field mappings still match API contract

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
