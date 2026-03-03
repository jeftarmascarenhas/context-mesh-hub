# Decision: UI Read-Only by Default

## Context

Context Mesh Hub includes a user interface to:
- visualize context artifacts
- guide users through Intent, Build, and Learn
- provide feedback, warnings, and insights
- orchestrate interaction with MCP and agents

In AI-assisted systems, UIs that allow direct mutation introduce risks:
- accidental context corruption
- bypassing governance rules
- implicit execution of actions
- loss of auditability

To preserve trust, the UI must prioritize **visibility, guidance, and safety**, not direct control.

## Decision

The Context Mesh Hub UI will operate in **read-only mode by default**.

All state-changing actions must:
- be explicitly requested
- require confirmation
- be mediated by MCP
- be traceable and auditable

The UI never performs silent or implicit mutations.

---

## Core Principles

1. **Visibility Over Control**
   - UI exists to reveal context, not manipulate it
   - Understanding precedes action

2. **Explicit Intentionality**
   - Every mutation starts with a clear user intent
   - No hidden side effects

3. **MCP as Authority Gate**
   - UI requests actions
   - MCP validates and executes
   - UI reflects outcomes

4. **Auditability**
   - All changes are attributable
   - UI displays provenance and status

---

## UI Capabilities

### Allowed by Default
- Browse intents, features, decisions, knowledge
- Visualize relationships and dependencies
- Inspect context bundles
- View build plans and execution logs
- Review learning drafts and evolution history

### Allowed with Explicit Action
- Propose new intents or features
- Propose decisions
- Trigger Plan / Approve / Execute modes
- Initiate Learn Sync
- Accept or reject learning drafts

### Never Allowed
- Silent execution
- Auto-apply changes
- Direct file mutation
- Background learning or syncing

---

## Interaction Flow

1. User explores context (read-only)
2. UI surfaces warnings, gaps, or inconsistencies
3. User explicitly requests an action
4. MCP validates request against rules and context
5. Agent performs action (if approved)
6. UI reflects outcome and logs

---

## Rationale

1. **Safety**
   - Prevents accidental destructive actions
   - Reduces blast radius of mistakes

2. **Trust**
   - Users understand what is happening and why
   - No “AI did something while I wasn’t looking”

3. **Enterprise Readiness**
   - Aligns with compliance and audit expectations
   - Separates visualization from execution

4. **Consistency**
   - Same behavior across CLI, UI, and chat
   - Single authority for mutations

---

## Alternatives Considered

### Alternative 1: Fully Editable UI
- **Pros**: fast, convenient
- **Cons**: unsafe, opaque
- **Rejected**: violates governance principles

### Alternative 2: Role-Based UI Mutations
- **Pros**: granular control
- **Cons**: complexity without clarity
- **Rejected**: premature optimization

### Alternative 3: Auto-Apply with Undo
- **Pros**: user-friendly
- **Cons**: undo ≠ intent
- **Rejected**: still hides decision points

---

## Consequences

- UI becomes a cognitive dashboard, not an editor
- Users gain confidence in system behavior
- MCP remains the single mutation authority
- Context integrity is preserved

---

## Related

- [Decision: Build Execution Modes](004-build-execution-modes.md)
- [Decision: Brownfield Context Extraction](005-brownfield-context-extraction.md)
- [Feature: Hub UI](../intent/feature-hub-ui.md)
- [Feature: Hub Learn Sync](../intent/feature-hub-learn-sync.md)

---

## Status

- **Created**: 2026-01-26
- **Status**: Accepted
