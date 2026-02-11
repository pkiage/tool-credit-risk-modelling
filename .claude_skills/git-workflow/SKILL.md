---
name: git-workflow
description: Reference guide for advanced git workflow patterns including worktrees, parallel development, and periodic cleanup. Use when setting up worktrees, doing parallel development, or cleaning up stale branches.
---

# Git Workflow Skill

Advanced git workflow patterns for the Credit Risk Platform monorepo. For basic branch naming, commit conventions, and the standard workflow, see CLAUDE.md.

## Periodic Cleanup

Run periodically (or at the start of a session) to catch accumulated stale branches and worktrees:

```bash
# 1. Check for stale worktrees
git worktree list                    # Should only show main worktree if no parallel work active

# 2. Remove any worktrees for merged PRs
git worktree remove ../credit-risk-[name]

# 3. Delete local branches whose PRs are merged
git branch                           # Review list
git branch -d [branch-name]          # -d is safe (refuses if unmerged)

# 4. Prune stale remote tracking refs
git remote prune origin
```

> **Tip:** If many branches have accumulated, check PR status with `gh pr list --state merged --json headRefName`.

## Parallel Development: Branches vs Worktrees

**Default**: Use branches. Only add worktrees when you need two working directories simultaneously.

### When to Use What

| Scenario | Use | Why |
|----------|-----|-----|
| Sequential feature work | Branch only | One task at a time, no extra setup |
| Quick fix while on a feature branch | Branch only | Stash, switch, fix, switch back |
| Working on `apps/api/` while testing `shared/` changes | Worktree | Need both running simultaneously |
| `apps/web/` + `apps/api/` dev in parallel | Worktree | Separate `node_modules` and `.venv` needed |
| Reviewing a PR while mid-feature | Worktree | Avoid stashing incomplete work |
| Long-running `docs/` + `feature/` tasks | Worktree | Independent streams, no context switching |

### Monorepo-Specific Notes

- **`shared/` changes cascade** to all apps — a worktree lets you test against apps without stash/switch cycles
- **Independent apps** (`apps/web/`, `apps/api/`, `apps/gradio/`) rarely conflict — parallel worktrees work well
- **`docs/`** is always safe for parallel worktrees since it never conflicts with code

## Worktree Commands

```bash
# Add a worktree for a new branch (from main)
git worktree add -b feature/api-auth ../credit-risk-api main

# Add a worktree for an existing branch
git worktree add ../credit-risk-docs docs/update-readme

# List all worktrees
git worktree list

# Remove a worktree (after merging/done)
git worktree remove ../credit-risk-docs
```

**Naming convention** for worktree directories: `../credit-risk-[purpose]`

```text
Dev/Repos/
├── tool-credit-risk-modelling/      <- main worktree (primary)
├── credit-risk-docs/                <- docs worktree
├── credit-risk-api/                 <- api feature worktree
└── credit-risk-web/                 <- web feature worktree
```

## Worktree Gotchas

| Gotcha | Detail |
|--------|--------|
| Same branch in two worktrees | **Not allowed.** Git prevents checking out the same branch in multiple worktrees. |
| Shared `.git` | All worktrees share one `.git` directory. Commits in any worktree are visible to all. |
| `node_modules` / `.venv` per worktree | Each worktree needs its own install. Run `npm install` and `uv sync` in each new worktree. |
| `.env` files | Not tracked by git. Copy `.env` manually to each new worktree. |
| Branch naming still applies | Worktree branches follow the same `feature/`, `fix/`, `docs/` convention. |
| Cleanup | Always use `git worktree remove`, not `rm -rf`. Stale entries break `git worktree list`. |

## Worktree + Branch Workflow

```bash
# 1. You're mid-feature on a branch. Need to start parallel work.

# 2. Create a worktree for the new task (branches from main)
git worktree add -b feature/new-task ../credit-risk-new-task main

# 3. Set up the new worktree
cd ../credit-risk-new-task
uv sync                         # Python deps
cd apps/web && npm install      # Node deps (if needed)

# 4. Work, commit, push, PR from the worktree
git push -u origin feature/new-task
gh pr create --title "feat(scope): description"

# 5. Clean up after merge
cd ../tool-credit-risk-modelling
git worktree remove ../credit-risk-new-task
```
