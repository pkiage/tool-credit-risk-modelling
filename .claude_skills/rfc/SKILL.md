---
name: rfc
description: Create, review, and edit Request for Comments (RFC) documents for technical proposals. Use when the user wants to write an RFC, design document, technical proposal, or feature specification. Also use when reviewing or providing feedback on existing RFCs, or when converting ideas into structured technical proposals.
---

# RFC Skill

Create well-structured RFC (Request for Comments) documents for technical proposals.

## When to Write an RFC

Not all code needs a design doc. Before drafting, assess whether an RFC is warranted.

**RFC likely warranted when:**

- The design is ambiguous or contentious and organizational consensus would be valuable
- Cross-cutting concerns exist (privacy, security, logging, observability)
- The project has non-obvious trade-offs worth documenting
- There's value in providing high-level insights into legacy systems
- Multiple engineers need to coordinate on implementation

**RFC likely NOT warranted when:**

- The solution is obvious and uncontroversial
- It's a small bug fix or minor refactor
- The change is well-understood and low-risk
- No coordination across teams is needed

**Skill behavior:** If the user's request suggests a straightforward change where an RFC may be overkill, ask whether they still want a formal RFC or if a lighter-weight approach (e.g., PR description, brief design notes) would suffice.

## RFC Structure

Every RFC should include these sections. Adapt depth based on proposal complexity.

### Required Sections

**1. Header Metadata**
Include at minimum: Title, Status, Author(s), Date. Optional: Sponsor, GitHub/Issue link, Supersedes/Obsoletes.

Status options: Draft → Proposed → Accepted → Implemented → Obsolete

**2. Objective**
Executive summary: what you're proposing and why. Keep to 2-3 sentences.

Include explicit **goals** and **non-goals**. Non-goals are not negated goals ("system shouldn't crash") but things that *could reasonably be goals* but are explicitly chosen not to be. This clarifies scope and prevents scope creep.

**3. Motivation**

- Why is this problem worth solving?
- Who is affected and how?
- What existing solutions fall short?
- Supporting data or evidence

**4. User Benefit**
How will users benefit? What would the release notes say? Keep concrete and user-focused.

**5. Design Proposal**
The core of the RFC. This is *the place to write down the trade-offs* you made in designing your solution. Don't just describe what—explain *why* this solution best satisfies the goals given the context.

Include:

- **System-context diagram** — Show how the new system fits into the larger technical landscape. Use Mermaid.js for diagrams (renders in GitHub, Notion, most doc platforms). Helps readers contextualize the design within systems they already know.
- **High-level approach** — Start with overview, then go into details.
- **Key design decisions and trade-offs** — Focus on *why*, not just *what*.
- **APIs** — If exposing an API, sketch it out. But resist copy-pasting verbose interface definitions; focus on parts relevant to design trade-offs.
- **Data storage** — How and where data is stored, if applicable.
- **Usage examples** — Concrete examples of how the feature will be used.

**6. Alternatives Considered**
What other approaches were evaluated? Why was this approach chosen? Be honest about tradeoffs.

### Conditional Sections

Include these when relevant to your proposal:

**Dependencies** - New dependencies introduced; projects that depend on this

**Engineering Impact** - Maintenance ownership, testability, build impact, API surface

**Platforms and Environments** - Compatibility with different platforms, devices, or execution environments

**Best Practices** - Changes to recommended practices; how to communicate them

**Tutorials and Examples** - Plans for documentation, tutorials, sample code

**User Impact** - User-facing changes, migration requirements

**Deprecation Plan** - How existing functionality will be phased out

**Detailed Design** - Technical deep-dive for complex proposals (can be separate document)

**Questions and Discussion Topics** - Open questions for reviewers to address

## Writing Guidelines

1. **Focus on trade-offs** — The design doc exists to document *why* you chose this solution. Given the context (facts), goals, and non-goals (requirements), show why this particular solution best satisfies those goals.

2. **Be specific** — Avoid vague language. Use concrete examples.

3. **Know your audience** — Write for both technical reviewers and stakeholders who need context.

4. **Front-load key information** — Objective and Motivation should stand alone as a summary.

5. **Use diagrams** — System-context diagrams help readers understand how the new design fits into the existing landscape.

6. **Don't over-document APIs** — Sketch relevant interfaces, but avoid verbose copy-paste of formal definitions that quickly go out of date.

7. **Acknowledge tradeoffs** — Honest discussion of alternatives builds trust.

8. **Keep it living** — Update status and content as the RFC progresses.

## Output Format

Create RFCs as Markdown (.md) files by default. For formal documents, create as Word (.docx) using the docx skill.

See `references/rfc-template.md` for a ready-to-use template.

## Example Objective Section

**Good:**
> Add a caching layer for database queries to reduce latency by 50% for repeated requests. Goals: sub-10ms response for cached queries, minimal memory overhead (<100MB). Non-goals: distributed caching (out of scope for v1), cache invalidation across services (handled by existing pub/sub).

**Weak:**
> Make the system faster by adding caching.

**Non-goals done right:**
Non-goals are things that *could* be goals but are explicitly scoped out. "The system shouldn't crash" is not a non-goal—that's just a requirement. "Supporting real-time sync" when you're building batch processing is a proper non-goal.
