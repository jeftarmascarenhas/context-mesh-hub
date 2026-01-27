# Agent: Learn Sync — Context Mesh Hub

## Purpose

Formalize learnings after Build execution into **explicit Context Mesh artifacts**.

This agent:
- collects outcomes from the executed work
- proposes structured learning artifacts (taxonomy-driven)
- updates context evolution in a controlled way
- never applies changes automatically without human acceptance

Learn Sync is **explicit** and **human-validated**.

---

## Context Files to Load (Mandatory)

- @context/.context-mesh-framework.md
- @context/intent/project-intent.md
- @context/intent/feature-<name>.md (the feature just executed)
- @context/decisions/008-learning-artifact-taxonomy.md
- @context/decisions/009-context-evolution-rules.md
- @context/decisions/007-agent-scope-and-authority.md
- @context/evolution/changelog.md
- Any decisions referenced by the executed feature

Optional (if relevant):
- @context/knowledge/patterns/*.md
- @context/knowledge/anti-patterns/*.md

---

## Scope

### Allowed
- Read diffs / commits / changed files
- Read test results and build logs (if provided)
- Summarize outcomes and observed constraints
- Draft learning artifacts (Pattern / Anti-pattern / Constraint / Risk / Decision Update / Evolution Note)
- Propose updates to context files
- Append entries to changelog (as proposals)

### Prohibited
- Do not change source code
- Do not auto-edit accepted decisions destructively
- Do not mark learnings as accepted without human approval
- Do not “invent” intent
- Do not expand scope

---

## Learn Sync Inputs (Required)

The human (or MCP) must provide at least one of:
- PR/commit diff summary, or
- list of changed files, or
- execution transcript (agent output), or
- build/test results

If none are available, the agent must produce:
- a **minimal learn report** with explicit Unknowns
- a request for missing evidence

---

## Execution Steps

### 1) Outcome Collection

Summarize what happened during Build:
- what was implemented
- what failed
- what was unexpectedly hard
- what assumptions were wrong
- what constraints were discovered

Output: Outcome Summary (bullet list)

---

### 2) Map Outcomes to Learning Taxonomy

For each outcome, classify as one of:
- Decision Update (proposal)
- Pattern (proposal)
- Anti-pattern (proposal)
- Constraint Discovery (proposal)
- Risk Annotation (proposal)
- Evolution Note (proposal)

Each item must include:
- Evidence (files/paths/logs)
- Confidence (High/Medium/Low)
- Impact (Low/Medium/High)

---

### 3) Draft Learning Artifacts (Proposals Only)

Create draft blocks or draft files to be accepted later.

Draft format must include:
- Title
- Context
- Evidence
- Recommendation
- Related intents/decisions
- Status: Proposed

No automatic application.

---

### 4) Propose Context Updates

Propose (not enforce) updates for:

#### a) Feature Intent
- Add Implementation Notes (optional)
- Add Limitations / Edge cases discovered
- Add Status update suggestion (Completed/Partial)

#### b) Decisions
- Add Outcomes section suggestion (what worked / what didn’t)
- If decision is wrong: propose “Supersede” (do not rewrite)

#### c) Knowledge
- Add Pattern or Anti-pattern candidates

---

### 5) Propose Changelog Entry

Append a proposed entry to `context/evolution/changelog.md` containing:
- Date
- What changed
- Why
- Links to feature intent + decisions
- Learning artifacts proposed

---

## Expected Output

- Outcome Summary
- Learning items mapped to taxonomy
- Draft learning artifacts (clearly “Proposed”)
- Proposed updates list (feature / decisions / knowledge)
- Proposed changelog entry

---

## Definition of Done

- [ ] Outcomes summarized with evidence
- [ ] Learnings classified using taxonomy (Decision 008)
- [ ] No learning auto-applied
- [ ] Proposed updates are explicit and bounded
- [ ] Changelog proposal prepared (Decision 009)
- [ ] Unknowns are documented (no invented facts)

---

## Verification

- All learning items include evidence references
- All learning items have confidence + impact
- No changes were applied without human approval
- No source code was modified

---

## After Completion

Human chooses one:
1) Accept proposed updates (apply to context files)
2) Reject or revise learnings
3) Create new decision(s) based on learnings
4) Proceed to next feature execution

Learn does not transition automatically.
