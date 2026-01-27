# Decision: Build Execution Modes

## Context

Context Mesh defines three macro phases:
- Intent
- Build
- Learn

However, during the Build phase, different teams and situations require **different levels of control** over how changes are executed.

In AI-assisted development, a single “execute now” approach creates risks:
- accidental large refactors
- unreviewed architectural changes
- loss of human accountability
- over-trusting agents in brownfield codebases

A structured execution model is required to:
- preserve human authority
- scale from exploratory work to enterprise-grade changes
- remain agent-agnostic

## Decision

The Context Mesh Hub will support **three explicit Build Execution Modes**:

1. **Plan**
2. **Approve**
3. **Execute**

These are **execution modes inside the Build phase**, not standalone phases.

The user always controls transitions between modes.

---

## Execution Modes

### 1. Plan Mode

**Purpose**
- Convert Intent + Context into an explicit implementation plan
- Surface assumptions, risks, and unknowns
- No code changes are allowed

**Characteristics**
- Read-only interaction with the codebase
- Produces structured plans (steps, files, risks)
- Highlights missing context or decisions
- Safe for exploration and brownfield analysis

**Outputs**
- Build plan draft
- Open questions
- Context gaps
- Risk indicators

---

### 2. Approve Mode

**Purpose**
- Human validation checkpoint before execution
- Enforce accountability and intentionality

**Characteristics**
- No code changes are allowed
- Plan is reviewed step-by-step
- Partial approval is allowed
- Rejection sends flow back to Plan mode

**Outputs**
- Approved execution scope
- Explicit go/no-go signals
- Execution boundaries

---

### 3. Execute Mode

**Purpose**
- Perform approved changes in the codebase

**Characteristics**
- Strictly bounded by approved plan
- No scope expansion allowed
- Execution is observable and traceable
- Failures do not auto-trigger retries or fixes

**Outputs**
- Code changes
- Execution logs
- Outcomes (success, partial, failed)

---

## Transition Rules

- Plan → Approve: explicit user action
- Approve → Execute: explicit user action
- Execute → Learn: optional, explicit
- No automatic transitions are allowed
- Skipping modes is allowed but discouraged and logged

---

## Constraints

- Execution modes are **advisory, not mandatory**
- Context Mesh does not enforce workflow rigidity
- Teams may choose:
  - Plan only
  - Plan + Execute
  - Full Plan → Approve → Execute
- All modes must be supported consistently across agents

---

## Rationale

1. **Human-in-the-Loop by Design**
   - Prevents silent or unintended changes
   - Keeps responsibility clear

2. **Enterprise Compatibility**
   - Mirrors real-world approval and change processes
   - Fits regulated environments

3. **Brownfield Safety**
   - Encourages analysis before action
   - Reduces blast radius in legacy systems

4. **Agent-Agnostic**
   - Works with Cursor, Copilot, Claude, or future agents
   - No dependency on agent-specific capabilities

---

## Alternatives Considered

### Alternative 1: Single Execute Mode
- **Pros**: simple
- **Cons**: unsafe, non-auditable
- **Rejected**: too risky for real projects

### Alternative 2: Full CI/CD-style Pipelines
- **Pros**: familiar to enterprises
- **Cons**: heavy, slow, tool-centric
- **Rejected**: Context Mesh is cognitive, not operational CI

### Alternative 3: Agent-Decided Execution
- **Pros**: faster
- **Cons**: removes human authority
- **Rejected**: violates core Context Mesh principles

---

## Consequences

- Execution becomes intentional, not reactive
- Agents behave as operators, not decision-makers
- Build phase remains flexible but governed
- Learn phase receives higher-quality signals

---

## Related

- [Decision: Context Bundling Strategy](003-context-bundling-strategy.md)
- [Feature: Hub Build Protocol](../intent/feature-hub-build-protocol.md)
- [Feature: Hub Brownfield](../intent/feature-hub-brownfield.md)
- [Feature: Hub Learn Sync](../intent/feature-hub-learn-sync.md)

---

## Status

- **Created**: 2026-01-26
- **Status**: Accepted
