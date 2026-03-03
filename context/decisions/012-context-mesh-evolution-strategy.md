# Decision 012: Context Mesh Evolution Strategy

## Context

Context Mesh Hub has grown from a framework concept to a concrete implementation with CLI, MCP server, and UI. With the core features in place, we needed to enhance the developer experience and ensure the system provides proactive guidance through the Intent → Build → Learn workflow.

Enhancements align with Context Mesh's identity:
- Slash commands in agent chat (Cursor, Copilot, Claude, Gemini)
- Quality gates for phase transitions
- Clarification before building
- Retrospectives for learning

## Decision

Evolve Context Mesh Hub with the following enhancements:

### 1. CLI Slash Commands
Add structured commands following the workflow phases:
- `/intent` - new-project, add-feature, fix-bug, update, create-agent
- `/build` - plan, approve, execute, clarify, gate
- `/learn` - sync, review, apply, retrospective

### 2. Proactive MCP Tools
Add tools that provide active intelligence:
- `cm_lifecycle_state` - Current phase with recommendations
- `cm_clarify` - Pre-build clarifying questions
- `cm_gate_check` - Quality gate verification
- `cm_suggest_next` - Next action suggestions
- `cm_workflow_guide` - Complete workflow status

### 3. Quality Gates System
Enforce checkpoints at phase transitions:
- **Intent → Build**: Feature complete, ADR exists, no validation errors
- **Build → Learn**: Implementation complete, tests pass, AC met

### 4. UI Enhancements
Add visualization and status components:
- MCP client library for API communication
- React hooks for data fetching
- Relationship graph (features ↔ decisions)
- Build dashboard with gate status
- Workflow status panel

### 5. Framework v1.2.0
New prompt templates:
- `clarify.md` - Pre-build clarification
- `checkpoint.md` - Gate verification
- `retrospective.md` - Post-implementation reflection

## Rationale

1. **CLI Slash Commands**: Provides structured workflows for terminal users while maintaining MCP as the authority gate. Users can choose their preferred interface (CLI, MCP, UI).

2. **Proactive MCP**: The MCP server becomes intelligent rather than merely reactive. It can guide users through the workflow and catch issues before they become problems.

3. **Quality Gates**: Prevents premature progress. A missing ADR caught at Gate 1 saves hours of rework. Gates enforce Context Mesh governance without being blocking.

4. **UI Enhancements**: Visual feedback helps users understand context relationships and current state. Read-only by design (Decision 006) but now with full read functionality.

5. **Framework v1.2.0**: New templates formalize patterns discovered during development. Clarification reduces ambiguity; retrospectives capture learnings.

## Alternatives Considered

1. **Adopt another product's slash commands verbatim**
   - Rejected: Would lose Context Mesh identity and introduce complexity
   - Instead: Slash commands and prompts are designed for Intent → Build → Learn

2. **Automatic gate enforcement (blocking)**
   - Rejected: Too rigid, would frustrate users
   - Instead: Gates warn and recommend but don't block

3. **Real-time UI updates via WebSocket**
   - Rejected: Adds complexity for v1
   - Instead: Polling with manual refresh, simpler to maintain

## Consequences

### Positive
- Users have multiple interfaces (CLI, MCP, UI) for same functionality
- Proactive guidance reduces errors and improves workflow
- Quality gates prevent costly mistakes
- Framework v1.2.0 provides better templates

### Trade-offs
- More code to maintain across three interfaces
- UI requires API route to communicate with MCP (extra hop)
- Quality gates add friction (intentionally)

### Risks
- CLI slash commands may conflict with shell escaping on some systems
- Proactive tools may be perceived as intrusive if too aggressive
- Gate checks may slow down experienced users

## Related

- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Feature: Hub UI](../intent/feature-hub-ui.md)
- [Decision: MCP Tool Contracts](./002-mcp-tool-contracts.md)
- [Decision: UI Readonly](./006-ui-readonly-by-default.md)
- [Decision: Prompt Pack Resolution](./010-prompt-pack-resolution-and-update-model.md)

## Status

- **Created**: 2026-01-31 (Phase: Build)
- **Status**: Accepted
