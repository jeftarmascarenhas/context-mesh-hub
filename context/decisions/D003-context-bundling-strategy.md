---
id: D003
type: decision
title: Context Bundling Strategy
status: accepted
created: 2026-03-04
updated: 2026-03-04
features: [F004]
supersedes: null
superseded_by: null
related: [D013]
---

# Decision: Context Bundling Strategy

## Context

Context Mesh Hub operates in environments where:
- repositories can be large (brownfield)
- multiple intents, features, decisions, and knowledge artifacts coexist
- AI agents have strict context window limits
- uncontrolled context injection leads to hallucinations, regressions, and incoherent builds

Traditional spec-driven tools treat context as a **flat, expanding prompt**, often resulting in:
- token explosion
- irrelevant information leakage
- loss of decision traceability
- brittle agent behavior

A formal strategy is required to **bundle, scope, and constrain context** before it is consumed by any agent.

## Decision

Context Mesh Hub will use a **deterministic, intent-scoped context bundling strategy** based on explicit references and bounded resolution.

Context is never implicitly loaded.

### Core Principles

1. **Intent-First Scoping**
   - Every bundle is rooted in a single Intent (project or feature)
   - No cross-intent leakage unless explicitly referenced

2. **Explicit Reference Resolution**
   - Only artifacts explicitly linked are eligible for inclusion
   - Links act as dependency declarations, not suggestions

3. **Bounded Expansion**
   - Each artifact type has a strict inclusion policy
   - Recursive expansion is limited and predictable

4. **Read-Only Bundles**
   - Bundles are immutable snapshots
   - No agent may mutate source artifacts during bundling

## Bundling Rules by Artifact Type

### Intent
- Always included
- Serves as bundle root
- Defines scope boundary

### Feature Intents
- Included only if explicitly referenced
- Treated as independent sub-roots
- Never auto-expanded by name similarity

### Decisions
- Included only when:
  - directly linked by the root intent or feature
  - or marked as `foundational` (e.g. 001-tech-stack)
- Decisions never reference features to avoid cycles

### Knowledge (Patterns / Anti-Patterns)
- Never auto-included
- Included only by explicit link
- Treated as advisory, not authoritative

### Agents
- Not bundled as context
- Referenced only as execution capabilities
- Instructions live outside the context bundle

### Codebase (Brownfield)
- Never fully bundled
- Accessed via:
  - summaries
  - extracted evidence
  - scoped file references
- Raw code included only when explicitly requested

## Bundle Assembly Phases

1. **Root Resolution**
   - Identify primary intent
   - Validate intent status and phase

2. **Reference Expansion**
   - Resolve direct links
   - Enforce artifact-type rules

3. **Constraint Validation**
   - Token budget estimation
   - Artifact count limits
   - Cycle detection

4. **Bundle Freezing**
   - Produce immutable snapshot
   - Assign bundle ID
   - Log bundle composition

## Rationale

1. **Predictability**
   - Same intent + same references = same bundle
   - Deterministic agent behavior

2. **Cognitive Load Control**
   - Prevents context flooding
   - Keeps agents focused on the actual problem

3. **Governance**
   - Context inclusion becomes an explicit design decision
   - Easier review and audit

4. **Brownfield Compatibility**
   - Scales to large repositories
   - Avoids naive “read the whole repo” patterns

## Alternatives Considered

### Alternative 1: Auto-Include Everything
- **Pros**: simple
- **Cons**: token explosion, hallucinations, non-determinism
- **Rejected**: not viable for real systems

### Alternative 2: Heuristic-Based Inclusion
- **Pros**: adaptive
- **Cons**: opaque, inconsistent, hard to debug
- **Rejected**: violates predictability principle

### Alternative 3: Prompt Compression Only
- **Pros**: reduces tokens
- **Cons**: loses intent and decision semantics
- **Rejected**: compression ≠ governance

## Consequences

- Context Mesh requires disciplined linking
- Poorly linked intents result in thin bundles (by design)
- Agents must ask for missing context explicitly
- Bundles become first-class artifacts for debugging

## Related

- [Decision: MCP Tool Contracts](002-mcp-tool-contracts.md)
- [Feature: Hub Brownfield](../intent/feature-hub-brownfield.md)
- [Feature: Hub Build Protocol](../intent/feature-hub-build-protocol.md)
- [Knowledge: Anti-Pattern – Context Flooding](../knowledge/anti-patterns/context-flooding.md)

## Status

- **Created**: 2026-01-26
- **Status**: Accepted
