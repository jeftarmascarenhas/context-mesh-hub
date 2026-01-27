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
- [ ] Build actions cannot proceed without an explicit plan
- [ ] Execution is blocked until approval is recorded
- [ ] Build plans reference the correct feature intent and decisions
- [ ] Execution instructions are generated deterministically
- [ ] Execution respects scope and constraints defined in the plan
- [ ] Approval status is visible to the user and agent

### Non-Functional
- [ ] Protocol is agent-agnostic (works with any MCP-compatible agent)
- [ ] No implicit execution is allowed by default
- [ ] Clear feedback is provided at each step (plan, approve, execute)
- [ ] Execution behavior is predictable and auditable
- [ ] Protocol does not require IDE-specific capabilities

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
- [Decision: Build Execution Modes](../decisions/006-build-execution-modes.md)
- [Decision: MCP Tool Contracts](../decisions/003-mcp-tool-contracts.md)

---

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Status**: Active
