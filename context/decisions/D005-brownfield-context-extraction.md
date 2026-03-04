---
id: D005
type: decision
title: Brownfield Context Extraction Strategy
status: accepted
created: 2026-03-04
updated: 2026-03-04
features: [F001]
supersedes: null
superseded_by: null
related: [D014]
---

# Decision: Brownfield Context Extraction Strategy

## Context

Context Mesh Hub must operate effectively on **existing (brownfield) codebases**, often characterized by:
- large repositories
- multiple architectural eras
- inconsistent documentation
- implicit business rules
- limited onboarding knowledge

Naive AI approaches attempt to:
- read the entire repository
- infer intent from code alone
- treat code as the primary source of truth

These approaches fail in real systems due to:
- context window limits
- loss of architectural intent
- hallucinated assumptions
- high risk of unintended changes

A deliberate strategy is required to extract **relevant, trustworthy, and scoped context** from brownfield systems.

## Decision

Context Mesh Hub will use a **progressive, evidence-based brownfield context extraction strategy**.

Code is treated as **evidence**, not intent.

Extraction is:
- scoped
- explicit
- incremental
- human-validated

---

## Core Principles

1. **Intent Does Not Emerge from Code**
   - Code reflects past decisions, not current intent
   - Intent must be reconstructed explicitly

2. **Progressive Disclosure**
   - Context is extracted in layers
   - No full-repo ingestion

3. **Evidence-Based Reasoning**
   - Claims must reference concrete code locations
   - Inference without evidence is flagged

4. **Human Validation Required**
   - Extracted context is always proposed, never authoritative

---

## Extraction Layers

### Layer 1: Structural Discovery
**Goal**: Understand shape, not meaning.

Includes:
- directory structure
- module boundaries
- entry points
- build and config files
- dependency graph

**Output**:
- high-level system map
- candidate domains
- potential feature boundaries

---

### Layer 2: Intent Reconstruction
**Goal**: Hypothesize intent from usage and patterns.

Includes:
- naming conventions
- public interfaces
- API routes
- domain models
- comments and docstrings

**Output**:
- proposed intents
- suspected responsibilities
- unclear or conflicting areas

---

### Layer 3: Decision Inference
**Goal**: Surface architectural and technical decisions.

Includes:
- framework usage patterns
- persistence strategies
- integration styles
- cross-cutting concerns

**Output**:
- proposed decisions
- inferred constraints
- technical trade-offs

---

### Layer 4: Risk & Fragility Detection
**Goal**: Identify danger zones before change.

Includes:
- highly coupled modules
- low test coverage areas
- deprecated or legacy patterns
- critical business paths

**Output**:
- risk annotations
- suggested safety boundaries
- recommended execution modes (Plan-only, etc.)

---

## Inclusion Rules

- Raw code is never fully bundled
- Code excerpts must be:
  - explicitly requested
  - scoped by file or symbol
  - justified by intent
- Summaries always link back to source files
- No speculative behavior without evidence markers

---

## Outputs as Context Artifacts

Brownfield extraction may produce:
- Feature Intents (proposed)
- Decisions (proposed)
- Knowledge patterns or anti-patterns
- Evolution notes documenting legacy constraints

All outputs start as **draft / proposed**.

---

## Rationale

1. **Scalability**
   - Works on monoliths and microservices
   - Independent of repo size

2. **Safety**
   - Minimizes blast radius
   - Avoids overconfident refactors

3. **Auditability**
   - Every inference is traceable
   - Easy to challenge or reject assumptions

4. **Alignment with Context Mesh Philosophy**
   - Context is curated, not scraped
   - Humans own meaning, AI assists discovery

---

## Alternatives Considered

### Alternative 1: Full Repository Ingestion
- **Pros**: simple
- **Cons**: impossible at scale, error-prone
- **Rejected**: unsafe and misleading

### Alternative 2: Heuristic Semantic Search Only
- **Pros**: fast
- **Cons**: shallow, context-fragmented
- **Rejected**: insufficient for intent reconstruction

### Alternative 3: Code-First Truth Model
- **Pros**: deterministic
- **Cons**: ignores business reality
- **Rejected**: code ≠ intent

---

## Consequences

- Brownfield onboarding becomes a first-class workflow
- AI agents act as investigators, not refactoring bots
- Context Mesh can evolve legacy systems safely
- Learning phase gains higher-quality signals

---

## Related

- [Decision: Context Bundling Strategy](003-context-bundling-strategy.md)
- [Decision: Build Execution Modes](004-build-execution-modes.md)
- [Feature: Hub Brownfield](../intent/feature-hub-brownfield.md)
- [Feature: Hub Build Protocol](../intent/feature-hub-build-protocol.md)
- [Knowledge: Anti-Pattern – Code-as-Truth](../knowledge/anti-patterns/code-as-truth.md)

---

## Status

- **Created**: 2026-01-26
- **Status**: Accepted
