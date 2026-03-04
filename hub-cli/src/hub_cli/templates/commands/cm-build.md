---
description: Run Build phase actions — plan, approve, execute, or check gates (Context Mesh).
handoffs:
  - label: Build plan
    agent: cm-build-plan
    prompt: Create an implementation plan for this feature.
  - label: Gate check
    agent: cm-gate-check
    prompt: Check intent-to-build or build-to-learn gate.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/cm-build` **is** the action or feature name — use it.

**If Context Mesh Hub MCP is available:** Choose the right action from the user's message and call `cm_build`:

- Create plan → `cm_build(action="plan", feature_name="<name>")`
- Approve plan → `cm_build(action="approve", plan_id="<id>")`
- Execute plan → `cm_build(action="execute", plan_id="<id>")`
- Bundle context → `cm_build(action="bundle", feature_name="<name>")`

For clarification or gate checks, use:
- Check gate → `cm_validate(gate="intent-to-build", feature_name="<name>")`
- Get status → `cm_status()`

If unclear, call `cm_status()` and suggest an action.

**If MCP is not available:** Load @context/.context-mesh-framework.md and the relevant feature + decisions. Follow Plan, Approve, Execute: produce a plan first, ask for approval, then implement only after approval. Do not skip planning or approval.

Report completion or the suggested next step.

## MCP Tool Reference (D013 Consolidated)

| Old Tool | New Tool Call |
|----------|---------------|
| build_plan | cm_build(action="plan") |
| build_approve | cm_build(action="approve") |
| build_execute | cm_build(action="execute") |
| context_bundle | cm_build(action="bundle") |
| cm_clarify | cm_validate(gate="clarity") |
| cm_gate_check | cm_validate(gate="...") |
| cm_status | cm_status() |
| cm_suggest_next | cm_status() |
