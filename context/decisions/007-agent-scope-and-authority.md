# Decision: Agent Scope and Authority

## Context

Context Mesh Hub integrates with multiple AI agents (Cursor, Copilot, Claude, etc.) to assist during Intent, Build, and Learn phases.

Without explicit boundaries, agents may:
- assume decision-making authority
- modify intent implicitly
- execute actions beyond user approval
- learn or adapt without validation

This creates loss of governance, unpredictability, and erosion of trust — especially in enterprise and brownfield environments.

A clear definition of **what agents can and cannot do** is required.

## Decision

AI agents in Context Mesh Hub operate strictly as **operators and assistants**, never as authorities.

All authority remains human-controlled and mediated through Context Mesh artifacts and MCP validation.

---

## Agent Capabilities

### Agents MAY
- Read context bundles provided by MCP
- Analyze codebases as evidence
- Generate drafts for:
  - build plans
  - decisions (proposed)
  - features (proposed)
  - learning artifacts (proposed)
- Execute code changes **only within an approved Build scope**
- Report execution results and failures

### Agents MUST NOT
- Create or modify authoritative intents
- Accept or finalize decisions
- Promote learning artifacts automatically
- Expand execution scope beyond approval
- Mutate context artifacts directly
- Execute actions without explicit user intent

---

## Authority Model

- **Humans**: Own intent, decisions, and learning acceptance
- **MCP**: Enforces rules, validates requests, orchestrates actions
- **Agents**: Perform bounded analysis and execution

Agents are interchangeable and non-authoritative by design.

---

## Rationale

1. **Governance**
   - Prevents AI overreach
   - Preserves accountability

2. **Predictability**
   - Same inputs produce consistent outcomes
   - No hidden agent behavior

3. **Enterprise Readiness**
   - Aligns with audit and compliance requirements
   - Supports regulated environments

4. **Future-Proofing**
   - New agents can be added without redefining trust boundaries

---

## Consequences

- Agents behave as tools, not decision-makers
- Human intent remains the primary driver
- Context integrity is preserved across cycles

---

## Related

- [Decision: Build Execution Modes](004-build-execution-modes.md)
- [Decision: UI Read-Only by Default](006-ui-readonly-by-default.md)
- [Feature: Hub Build Protocol](../intent/feature-hub-build-protocol.md)

---

## Status

- **Created**: 2026-01-26
- **Status**: Accepted
