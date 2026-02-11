---
name: changelog
description: Maintain and update the project CHANGELOG.md. Use when merging PRs, preparing releases, when the user asks to update the changelog, add changelog entries, or review changelog quality.
---

# Changelog Skill

Maintain `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format with project-specific conventions.

## When to Update the Changelog

**Add an entry for every PR that:**

- Adds, changes, or removes user-facing behavior
- Fixes a bug
- Changes dependencies that affect runtime behavior
- Modifies the API surface (endpoints, schemas, request/response shapes)
- Changes deployment configuration that affects how the app runs

**Do NOT add entries for:**

- Documentation-only PRs (README, ADR, RFC updates)
- CI-only changes (workflow tweaks, linting config)
- Internal refactors that do not change observable behavior
- Test-only changes

**Gray areas:** If a CI change enables a new deployment target (e.g., adding a Dockerfile for Cloud Run), that IS changelog-worthy under Infrastructure. Use judgment — if a user or operator would care, include it.

## Entry Format

```
- [scope] Brief imperative description (#PR)
```

### Rules

1. **Scope** matches the conventional commit scopes used in this project: `shared`, `api`, `web`, `gradio`, `marimo`, `ci`, `chore`
2. **Description** uses imperative mood, present tense: "Add dark mode toggle" not "Added dark mode toggle"
3. **PR number** at the end in parentheses. Multiple PRs OK: `(#38, #39)`
4. **One entry per PR** unless the PR genuinely does multiple independent things
5. **Focus on what changed for the user**, not implementation details

### Examples

**Good:**

```
- [web] Add dark mode toggle with system preference detection (#46)
- [api] Fix rate limiter bypassing on preflight requests (#39)
- [shared] Add automatic feature selection: Boruta, Lasso, Tree Importance, WOE-IV (#38)
```

**Bad:**

```
- Added dark mode                              # No scope, no PR, vague
- feat(web): add dark mode toggle (#46)        # Commit message format, not changelog
- [web] Refactored CSS class naming (#46)      # Internal detail, not user-facing
- Fixed bug                                    # Useless
```

## Section Placement

Place entries in `[Unreleased]` under the correct Keep a Changelog category:

| Section | Use for |
|---------|---------|
| **Added** | New features, endpoints, pages, deployment targets |
| **Changed** | Changes to existing functionality, dependency upgrades, behavior changes |
| **Deprecated** | Features marked for future removal |
| **Removed** | Features that were removed |
| **Fixed** | Bug fixes |
| **Security** | Vulnerability fixes, security improvements |

### Sub-grouping (initial releases only)

For large initial releases (like 0.1.0), the Added section may use sub-headings by layer:

```markdown
### Added

#### Shared Layer (`shared/`)
- [shared] ...

#### API Layer (`apps/api/`)
- [api] ...
```

Do NOT use sub-headings for ongoing releases — they add noise when there are only a few entries per section.

## Release Workflow

When cutting a release:

1. Move all `[Unreleased]` entries to a new versioned section `[X.Y.Z] - YYYY-MM-DD`
2. Add a fresh empty `[Unreleased]` section above
3. Verify the version matches `pyproject.toml` and `apps/web/package.json`
4. Add comparison links at the bottom of the file (if using GitHub releases)

## Backfill Guidance

When catching up on missed entries:

```bash
# List all merged PRs not yet in the changelog
gh pr list --state merged --json number,title,mergedAt --limit 100
```

Cross-reference with existing CHANGELOG.md entries. For each missing PR, evaluate whether it meets the "when to update" criteria above.

## Quality Checklist

Run through this before finalizing changelog updates:

- [ ] Every entry has a `[scope]` prefix
- [ ] Every entry has a PR number reference `(#NN)`
- [ ] Entries use imperative mood
- [ ] No duplicate entries across sections
- [ ] Entries are under the correct category (Added/Changed/Fixed/etc.)
- [ ] `[Unreleased]` section exists at the top
- [ ] No entry appears in both Unreleased and a versioned section
- [ ] Removed entries are in Changed (if replaced) or Removed (if deleted)

See `references/changelog-template.md` for the standard file structure.
