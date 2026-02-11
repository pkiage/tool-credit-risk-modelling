---
name: adr
description: Create Architecture Decision Records (ADRs). Use when the user wants to record an architectural decision, document a technical choice, or when creating a new ADR for a PR.
---

# ADR Skill

Create well-structured Architecture Decision Records for the Credit Risk Platform.

## When to Write an ADR

**ADR warranted when:**

- Choosing between technologies, libraries, or patterns
- Making a decision that constrains future options
- Removing or replacing existing functionality
- Choosing a deployment strategy or infrastructure pattern
- Any decision someone might later ask "why did we do it this way?"

**ADR NOT warranted when:**

- The choice is obvious and uncontroversial (e.g., using pytest for Python tests)
- It's a temporary decision that will be revisited soon
- The decision is purely cosmetic (formatting, naming that follows existing conventions)

## Creation Steps

### 1. Pick the next number

```bash
# Check the highest ADR number on main (not your branch)
ls docs/1-ADRs/ADR-*.md | sort -V | tail -1
```

**Conflict avoidance** (when working in parallel):

- Check open PRs for new ADR files: `gh pr list --search "ADR" --state open`
- If a conflict is found at merge time, renumber the later PR's ADR
- Never reuse a number that appeared in a merged PR, even if the file was later deleted

### 2. Create the file

File: `docs/1-ADRs/ADR-NNN-short-description.md`

Use the template in `references/adr-template.md`.

Required metadata table:

```markdown
# ADR-NNN: Title

| Field | Value |
|-------|-------|
| Status | Proposed |
| Author | Paul / Claude |
| Date | YYYY-MM-DD |
| PR | _Added before merge_ |
```

Status lifecycle: `Proposed` -> `Accepted` -> `Superseded` (or `Rejected`)

### 3. Write the content

Focus on:

- **Context**: What situation or problem prompted this decision?
- **Decision**: What did we decide? Be specific.
- **Consequences**: What are the trade-offs? What becomes easier/harder?
- **Alternatives**: What else was considered and why was it rejected?

### 4. Before merging the PR

- [ ] Add the `| PR |` link to the ADR metadata table
- [ ] Add the new ADR to `docs/1-ADRs/ADR-README.md` index table
- [ ] Verify no numbering conflict with other open/recently-merged PRs

## ADR Quality Guidelines

**Good ADRs:**

- Explain the "why" — future readers need context, not just the conclusion
- Are honest about trade-offs — every decision has downsides
- Are concise — 1-2 pages is ideal; if longer, the decision may need splitting
- Stand alone — a reader shouldn't need to read other docs to understand this one

**Bad ADRs:**

- Just state the decision with no context or alternatives
- Read like a tutorial or how-to guide (that belongs in docs/)
- Are so long they'll never be read

## Example

**Good context section:**
> We need to choose a chart library for the Next.js production UI. The app displays ROC curves, calibration plots, and confusion matrices. We need responsive, accessible charts that work with React 19 and support dark mode.

**Weak context section:**
> We need charts.

See `references/adr-template.md` for the full template.
