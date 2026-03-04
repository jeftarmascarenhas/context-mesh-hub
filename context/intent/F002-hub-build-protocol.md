---
id: F002
type: feature
title: Hub Build Protocol (Plan / Approve / Execute)
status: in-progress
priority: high
created: 2026-03-04
updated: 2026-03-04
depends_on: [F004]
decisions: [D004]
agents: []
---

# Feature Intent: Hub Build Protocol (Plan / Approve / Execute)

## What

Introduce a **Build governance protocol** inside the Context Mesh lifecycle that structures how changes are planned, reviewed, and executed during the **Build phase**.

The protocol is composed of three explicit steps:

- **Plan** — propose how the intent will be implemented
- **Approve** — give human authorization to proceed
- **Execute** — perform the change, guided by context

This protocol exists to preserve **human authority, traceability, and control** in AI-assisted development.

---

## Why

**Business Value**
- Prevents uncontrolled or accidental changes in critical systems
- Makes AI-assisted development auditable and reviewable
- Reduces risk when working in large or regulated codebases
- Aligns AI-assisted workflows with enterprise governance expectations

**Technical Value**
- Separates intent definition from implementation execution
- Creates a clear decision boundary before code changes occur
- Enables consistent execution behavior across different agents
- Reduces ambiguity and rework caused by premature execution

---

## Scope

### Build Phase Governance
- Apply only within the **Build** phase of the Context Mesh lifecycle
- Do not redefine or replace lifecycle phases
- Act as an execution protocol, not a workflow engine

### Plan
- Generate an explicit build plan based on:
  - Feature intent
  - Related decisions
  - Constraints and acceptance criteria
- The plan must:
  - Describe *what* will be changed
  - Describe *where* changes will occur
  - Avoid implementation until approved

### Approve
- Require explicit human confirmation before execution
- Support:
  - Full approval
  - Partial approval
  - Rejection with feedback
- Approval is a **decision checkpoint**, not an automation step

### Execute
- Execute changes **only after approval**
- Execution can occur in two modes:
  - Instruction-based execution (default)
  - Assisted execution (explicitly enabled)
- Execution must respect all approved constraints and decisions

---

## Acceptance Criteria

### Functional
- [x] Build actions cannot proceed without an explicit plan
- [x] Execution is blocked until approval is recorded
- [x] Build plans reference the correct feature intent and decisions
- [x] Execution instructions are generated deterministically
- [x] Execution respects scope and constraints defined in the plan
- [x] Approval status is visible to the user and agent

### Non-Functional
- [x] Protocol is agent-agnostic (works with any MCP-compatible agent)
- [x] No implicit execution is allowed by default
- [x] Clear feedback is provided at each step (plan, approve, execute)
- [x] Execution behavior is predictable and auditable
- [x] Protocol does not require IDE-specific capabilities

---

## Execution Modes

### Instruction-Based Execution (Default)
- MCP emits structured execution instructions
- AI agent performs the changes in the chat or IDE
- Safest and most portable mode
- Works across all MCP-compatible environments

### Assisted Execution (Optional)
- MCP exposes additional helper tools during execution
- Tools may include:
  - Context-aware file creation
  - Reference validation
  - Post-execution checks
- Must be explicitly enabled by the user
- Still requires prior approval

---

## Implementation Approach

1. **Plan Generation**
   - Generate a build plan from validated context
   - Include:
     - Target files or modules
     - Constraints and non-goals
     - Validation steps

2. **Approval Recording**
   - Capture approval decision explicitly
   - Store approval state as part of the build context
   - Support revisions to the plan before approval

3. **Execution Instruction Emission**
   - Generate clear, scoped execution instructions
   - Avoid embedding IDE-specific commands
   - Include post-execution validation guidance

4. **Execution Guardrails**
   - Enforce:
     - Scope boundaries
     - Decision constraints
     - Acceptance criteria awareness

---

## Constraints

- **Human-in-the-loop required**: no autonomous execution
- **Protocol over workflow**: no enforced task engines
- **Agnostic execution**: no dependency on specific IDEs or agents
- **Safety first**: execution must never exceed approved scope

---

## Related

- [Project Intent](./project-intent.md)
- [Feature: Hub Core](./feature-hub-core.md)
- [Feature: Hub Brownfield](./feature-hub-brownfield.md)
- [Decision: Build Execution Modes](../decisions/004-build-execution-modes.md)
- [Decision: MCP Tool Contracts](../decisions/002-mcp-tool-contracts.md)
- [Decision: Prompt Pack Resolution and Update Model](../decisions/010-prompt-pack-resolution-and-update-model.md)

---

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Completed**: 2026-01-27 (Phase: Build)
- **Status**: Completed

## Implementation Notes

Hub Build Protocol has been implemented as an extension to Hub Core MCP server.

### Components Implemented

1. **Build Protocol Core** (`build_protocol.py`)
   - `BuildPlan` - Structured plan representation
   - `ApprovalState` - Approval status management
   - `ExecutionInstruction` - Structured execution instructions
   - `BuildProtocol` - Main protocol logic
   - Plan generation from feature intents
   - Approval state management (full/partial/reject)
   - Instruction generation from approved plans

2. **MCP Tools** (extended `tools.py`)
   - `build_plan` - Generate execution plans from feature intents
   - `build_approve` - Approve or reject build plans
   - `build_execute` - Generate execution instructions from approved plans

### Features

- **Plan Generation**: Extracts implementation steps, constraints, and acceptance criteria from feature intents
- **Approval Workflow**: Supports full approval, partial approval (by step), and rejection with feedback
- **Execution Gating**: Execution instructions only generated for approved plans
- **Instruction Format**: Agent-agnostic structured format (no IDE-specific commands)
- **State Management**: In-memory state storage (plans and approvals)

### Verification

- ✅ Plan generation works for features
- ✅ Approval workflow (approve/reject) works correctly
- ✅ Execution blocked without approval
- ✅ Instructions generated deterministically
- ✅ All Acceptance Criteria met

### Limitations

- State is in-memory only (lost on server restart)
- Plan versioning not implemented
- No persistence layer (can be added later if needed)
