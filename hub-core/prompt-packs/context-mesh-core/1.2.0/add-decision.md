# Prompt: Add Decision (ADR)

Use this prompt to create a **standalone technical decision** (ADR – Architectural Decision Record) in a Context Mesh project.

**When to use:**
- Creating a decision **without** adding a feature (e.g. tech stack, cross-cutting choice)
- Documenting a technical approach **before** or **after** a feature exists
- Adding an ADR when the user says "we decided to use X" and you need to capture it in context

**What is a decision?** A documented technical choice: context, chosen approach, rationale, alternatives. It is **not** a spec (what to build) or a task list (what to do next). It answers **how** and **why** we build it that way.

---

## How to Use

1. **Copy** the prompt below
2. **Paste** in your AI assistant (Cursor, Copilot, Claude, etc.)
3. **Answer** the questions
4. **Review** the generated decision file
5. **Link** to related features or project intent if applicable

---

## Prompt

```
Add a new technical decision (ADR) to this Context Mesh project.

**FIRST: Load framework context:**
- Load @context/.context-mesh-framework.md (if exists) to understand Context Mesh rules and decision file structure
- Check @context/decisions/ for existing decisions and the next number (e.g. 001, 002, 003)

**Then ask me:**

**Decision Information:**
1. What decision needs to be made? (short title, e.g. "Tech Stack", "Auth Approach")
2. What is the context? (situation, requirements, constraints)
3. What approach did you choose?
4. Why this approach? (rationale – reasons for choosing)
5. What alternatives did you consider? (and why not chosen)
6. What are the consequences? (positive outcomes and trade-offs)
7. Is this decision related to a feature? (if yes: which feature – link in Related section)
8. Is this decision related to project intent? (link in Related section)

**Then create:**
- context/decisions/[next-number]-[slug].md
  - Use the next number (001, 002, 003…) and a slug from the title (e.g. 002-auth-approach)
  - Include: Context, Decision, Rationale, Alternatives Considered, Consequences, Related, Status
  - In **Related**: link to [Project Intent](../intent/project-intent.md) and [Feature: X](../intent/feature-x.md) if applicable
- Update context/evolution/changelog.md with the new decision
- If linked to a feature: update that feature's **Related** section with [Decision: Title](../decisions/[number]-[slug].md)

**Bidirectional links:** If this decision is for a feature, the feature file MUST link to this decision and this decision MUST link back to the feature.

**Status:** Set Status to "Proposed" until the approach is accepted; then "Accepted".

**Key principle:** Decisions are immutable once accepted. Evolve via supersession (new decision that supersedes this one), not by rewriting.
```

---

## Execute: Use the Decision

After the decision file exists, implementation should follow it:

```
When implementing, load @context/decisions/[number]-[slug].md and follow the documented approach.
Do not deviate from the decision without creating a new (superseding) decision.
```

---

## What This Prompt Does

- **Creates a standalone ADR** – Not tied to add-feature flow; use for tech stack, cross-cutting choices, or any "we decided to…" moment
- **Follows framework structure** – Context, Decision, Rationale, Alternatives, Consequences, Related, Status
- **Maintains links** – Bidirectional links to project intent and related features when applicable
- **Updates changelog** – Records the new decision in evolution

**Difference from add-feature.md:** add-feature.md creates **feature intent + decision together** (one decision per feature). This prompt creates **only the decision**, for when you need an ADR without a new feature (e.g. "we decided to use PostgreSQL", "we decided on REST over GraphQL").

---

## Related Prompts

- **add-feature.md** – Creates feature + decision together (use when adding a new feature)
- **update-feature.md** – Updates or adds a decision when changing a feature
- **fix-bug.md** – Optionally creates a decision for a significant technical change
- **learn-update.md** – Updates decision **Outcomes** after implementation

---

## Context Mesh Artifacts (Reminder)

| Artifact | Purpose |
|----------|---------|
| **Feature intent** | **What** to build, why, acceptance criteria |
| **Decision (ADR)** | **How** we chose to build it; first-class in Context Mesh |
| **Build plan steps** | **What to do** next (steps, files); execution list |

A **decision** in Context Mesh is **not** a feature spec (we have feature intent for that) and **not** a task list (we have build plan for that). It is the documented **technical choice** (approach, rationale, alternatives) that guides implementation.
