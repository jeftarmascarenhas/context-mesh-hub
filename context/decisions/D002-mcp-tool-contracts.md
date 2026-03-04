---
id: D002
type: decision
title: MCP Tool Contracts
status: accepted
created: 2026-03-04
updated: 2026-03-04
features: [F004]
supersedes: null
superseded_by: D013
related: []
---

# Decision: MCP Tool Contracts

## Context

Context Mesh Hub is designed as an **MCP-first system** that must operate consistently across:
- CLI
- Local UI
- Chat-based AI agents
- IDE-integrated agents (Cursor, Copilot, Claude, etc.)

To ensure predictability, safety, and agent-agnostic behavior, the Hub requires **explicit, stable tool contracts** for all MCP interactions.

Without defined contracts:
- tools become implicit prompts
- agents behave inconsistently
- governance guarantees break down

## Decision

Context Mesh Hub will expose a **small, explicit, versioned set of MCP tools** that act as the sole interface to domain behavior.

All clients (CLI, UI, agents) must interact **only through these tools**.

### Core Tool Categories

#### 1. Context Inspection
Tools that allow reading and understanding context state.

Examples:
- `context.status`
- `context.list`
- `context.validate`
- `context.graph`

Characteristics:
- Read-only
- Deterministic
- Safe by default

#### 2. Build Governance
Tools that support the Build Protocol.

Examples:
- `build.plan`
- `build.approve`
- `build.execute`

Characteristics:
- Explicit inputs
- Clear preconditions
- Execution guarded by approval state

#### 3. Learning & Evolution
Tools that support explicit learning.

Examples:
- `learn.propose`
- `learn.review`
- `learn.sync`

Characteristics:
- Never automatic
- Always produce proposed artifacts first
- Require human confirmation

#### 4. Diagnostics
Tools that support observability and safety.

Examples:
- `hub.health`
- `hub.doctor`
- `hub.capabilities`

## Rationale

1. **Agent-Agnosticism**
   - MCP tools provide a stable interface regardless of agent implementation
   - Prevents lock-in to Cursor, Copilot, or any single vendor

2. **Safety**
   - Tool boundaries prevent accidental execution
   - Explicit inputs reduce hallucinated actions

3. **Auditability**
   - All meaningful actions pass through known tools
   - Enables logging, inspection, and reasoning

4. **Composability**
   - CLI and UI are thin layers on top of the same contracts
   - Reduces duplicated logic and divergence

## Alternatives Considered

### Alternative 1: Prompt-Only Interface
- **Pros**: simpler to prototype
- **Cons**: ambiguous, unsafe, non-deterministic
- **Rejected**: breaks governance and predictability

### Alternative 2: IDE-Specific APIs
- **Pros**: richer UX in specific editors
- **Cons**: fragmentation, lock-in
- **Rejected**: violates agent-agnostic goal

## Consequences

- All domain logic must live behind MCP tools
- UI and CLI cannot bypass MCP
- Tool contracts must be versioned carefully
- Backward compatibility becomes a first-class concern

## Related

- [Decision: Tech Stack](001-tech-stack.md)
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: Hub UI](../intent/feature-hub-ui.md)
- [Feature: Hub Build Protocol](../intent/feature-hub-build-protocol.md)

## Status

- **Created**: 2026-01-26
- **Status**: Accepted
