# Decision: Learning Artifact Taxonomy

## Context

The Learn phase of Context Mesh captures insights generated during execution.

Without structure, learnings become:
- unstructured logs
- vague feedback
- non-reusable notes

This reduces long-term value and prevents agents and humans from leveraging past outcomes effectively.

A formal taxonomy is required to classify, validate, and reuse learning consistently.

## Decision

Context Mesh Hub will classify all learnings into **explicit learning artifact types**.

Learning artifacts are proposed, reviewed, and accepted before becoming authoritative.

---

## Learning Artifact Types

### Decision Update
- Refines, supersedes, or deprecates an existing decision
- Always references the original decision

### Pattern
- A practice or structure that proved effective
- Intended for reuse across features or projects

### Anti-Pattern
- A practice that caused issues or risk
- Explicitly documented to prevent repetition

### Constraint Discovery
- Newly identified technical or organizational limitation
- Impacts future intent or build choices

### Risk Annotation
- Identifies fragile or high-risk areas
- Used to guide Build execution modes

### Evolution Note
- Records historical change without prescribing behavior
- Supports long-term traceability

---

## Rules

- Every learning artifact must:
  - reference a concrete execution or outcome
  - specify its artifact type
  - link to related intents or decisions
- No learning is auto-applied
- Reclassification is allowed through explicit evolution

---

## Rationale

1. **Clarity**
   - Learning becomes actionable, not anecdotal

2. **Reusability**
   - Patterns and anti-patterns compound value over time

3. **Agent Reasoning**
   - Structured learnings improve future planning and analysis

4. **Governance**
   - Prevents silent or ambiguous system evolution

---

## Consequences

- Learn phase produces durable cognitive assets
- Context Mesh becomes progressively smarter without losing control
- Learning quality improves with project maturity

---

## Related

- [Feature: Hub Learn Sync](../intent/feature-hub-learn-sync.md)
- [Decision: Context Evolution Rules](009-context-evolution-rules.md)

---

## Status

- **Created**: 2026-01-26
- **Status**: Accepted
