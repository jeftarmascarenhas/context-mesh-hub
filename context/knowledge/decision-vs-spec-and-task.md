# Decision vs Spec and Task

## Short Answer

- **Decision (Context Mesh) ≠ Spec.** Our **feature intent** is the spec (what to build, why, acceptance criteria).
- **Decision (Context Mesh) ≠ Task.** Our **build plan steps** are the task list (what to do next).
- **Decision** in Context Mesh is a **first-class ADR**: the documented technical choice (how and why we build it that way). It is a separate artifact; technical choices are not buried inside a spec or plan.

---

## Context Mesh Artifacts

| Artifact | Purpose | Answers |
|----------|---------|---------|
| **Feature intent** | What to build, why, acceptance criteria | **What** and **why** we build it |
| **Decision (ADR)** | Technical approach, rationale, alternatives | **How** we chose to build it and **why this approach** |
| **Build plan** | Implementation steps, target files, constraints | **What to do** next (steps, order) |
| **Learn / outcomes** | What happened after implementation | **What we learned** |

---

## Why We Have a Dedicated Decision Prompt

1. **Standalone ADRs** – Tech stack, cross-cutting choices (“we use PostgreSQL”, “we use REST”) don’t always belong to a single feature. **add-decision.md** creates an ADR without going through add-feature.
2. **Symmetry** – We have **add-feature.md**, **new-project.md**; having **add-decision.md** keeps the framework consistent.
3. **Tool + prompt** – The MCP tool **cm_create_decision** exists; the prompt gives the same flow in copy-paste form and documents the structure (Context, Decision, Rationale, Alternatives, Related, Status).
4. **Identity** – Context Mesh treats “how we decided” as a first-class artifact; a dedicated decision prompt reinforces that.

---

## Summary

| Question | Answer |
|----------|--------|
| Is a decision the same as a feature spec? | **No.** Our **feature intent** is the spec. Decision is the **technical choice** (ADR). |
| Is a decision the same as a task list? | **No.** Our **build plan steps** are the tasks. Decision is **how** we chose to implement, not the task list. |
| Do we have a decision prompt in the framework? | **Yes.** **add-decision.md** in prompt-packs (1.0.0 and 1.2.0). Use for standalone ADRs; use **add-feature.md** when adding feature + decision together. |
