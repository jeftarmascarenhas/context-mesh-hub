# Decision: Context Evolution Rules

## Context

Context Mesh Hub manages context artifacts that evolve over time as:
- features are implemented and completed
- decisions are refined or superseded
- learnings are captured and validated
- new constraints and patterns are discovered

Without explicit rules, context evolution becomes:
- inconsistent
- hard to trace
- prone to silent mutations
- unreliable for agents and humans

A formal set of evolution rules is required to ensure context remains:
- auditable
- traceable
- immutable in history
- explicitly governed

## Decision

Context Mesh Hub will enforce **strict evolution rules** that govern how context artifacts change over time.

All evolution is:
- explicit
- human-validated
- recorded in changelog
- traceable to outcomes

---

## Core Principles

1. **Context Never Mutates Silently**
   - No automatic updates
   - No background learning
   - All changes require explicit human intent

2. **History is Immutable**
   - Past context artifacts are never rewritten
   - Evolution is additive, not destructive
   - Changelog preserves complete history

3. **Decisions are Superseded, Not Rewritten**
   - Original decision remains in place
   - New decision references and supersedes the old
   - Both decisions remain accessible for traceability

4. **Features Evolve Through Status**
   - Features may be: Active, Completed, Replaced, or Abandoned
   - Status changes are recorded in changelog
   - Completed features remain as historical record

5. **Learning Always References Concrete Outcomes**
   - No speculative learnings
   - All learnings must link to execution results
   - Evidence is required for acceptance

---

## Evolution Rules by Artifact Type

### Intent (Project & Feature)

**Allowed Changes:**
- Status updates (Active → Completed/Replaced/Abandoned)
- Adding learnings or limitations sections
- Updating acceptance criteria (with changelog entry)
- Adding related links

**Prohibited:**
- Rewriting original What/Why without supersession
- Removing historical content
- Silent status changes

**Evolution Method:**
- Status changes recorded in changelog
- Major changes may require new feature intent (supersession)

---

### Decisions

**Allowed Changes:**
- Creating new decision that supersedes an existing one
- Adding "Outcomes" or "Consequences" sections to existing decisions
- Marking decisions as "Deprecated" or "Superseded by NNN-*"

**Prohibited:**
- Rewriting accepted decisions
- Removing original rationale
- Changing decision number or core content

**Evolution Method:**
- **Supersession**: Create new decision (e.g., `010-*.md`) that references the old
- Original decision remains unchanged
- New decision explicitly states what it supersedes
- Both decisions remain in context bundles when referenced

---

### Knowledge (Patterns & Anti-Patterns)

**Allowed Changes:**
- Adding new patterns/anti-patterns
- Refining existing ones with evidence
- Linking to new decisions or features

**Prohibited:**
- Removing patterns without deprecation
- Rewriting without evidence

**Evolution Method:**
- New patterns added as new files
- Existing patterns refined with version notes or supersession
- Deprecated patterns marked but not deleted

---

### Evolution (Changelog)

**Required for All Evolution:**
- Date of change
- What changed
- Why it changed
- References to related intents/decisions
- Who initiated (human or agent with human approval)

**Changelog Structure:**
- Chronological entries
- Grouped by date
- Links to related artifacts
- Clear distinction between proposed and accepted changes

---

## Learning Integration Rules

When learnings are accepted:

1. **Decision Updates**
   - Create new decision that supersedes
   - Original decision marked as superseded
   - Both remain accessible

2. **Patterns/Anti-Patterns**
   - Add new knowledge artifact
   - Link from originating feature/decision
   - Include evidence references

3. **Evolution Notes**
   - Append to changelog
   - Link to originating feature
   - Reference concrete outcomes

4. **Constraint Discovery**
   - Update relevant feature intents (add to Constraints)
   - May trigger new decision if architectural
   - Record in changelog

---

## Prohibited Evolution Behaviors

The following are explicitly forbidden:

- Silent mutations (changes without changelog)
- Rewriting history (editing old artifacts destructively)
- Auto-learning (background adaptation)
- Agent-driven evolution without human approval
- Removing context artifacts (only deprecate)
- Changing decision numbers or file names
- Implicit status changes

---

## Rationale

1. **Auditability**
   - Complete history enables review and compliance
   - Traceability supports debugging and reasoning

2. **Trust**
   - Immutable history prevents confusion
   - Explicit evolution builds confidence

3. **Agent Reliability**
   - Predictable evolution enables better agent reasoning
   - Clear rules prevent hallucinated changes

4. **Enterprise Readiness**
   - Aligns with governance expectations
   - Supports regulated environments

---

## Consequences

- Context artifacts accumulate over time (by design)
- Supersession creates decision chains (original → new)
- Changelog becomes comprehensive historical record
- Agents must respect immutability rules
- Human review required for all evolution

---

## Related

- [Decision: Learning Artifact Taxonomy](008-learning-artifact-taxonomy.md)
- [Feature: Hub Learn Sync](../intent/feature-hub-learn-sync.md)
- [Context Mesh Framework](../.context-mesh-framework.md)

---

## Status

- **Created**: 2026-01-27
- **Status**: Accepted
