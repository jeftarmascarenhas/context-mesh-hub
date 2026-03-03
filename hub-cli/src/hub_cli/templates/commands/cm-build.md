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

**If Context Mesh Hub MCP is available:** Choose the right tool from the user's message:
- Create plan → `build_plan(feature_name)`
- Approve plan → `build_approve(plan_id)`
- Execute plan → `build_execute(plan_id)`
- Clarify feature → `cm_clarify(feature_name)`
- Check gate → `cm_gate_check("intent-to-build", feature_name)`
If unclear, call `cm_status` or `cm_suggest_next` and suggest an action.

**If MCP is not available:** Load @context/.context-mesh-framework.md and the relevant feature + decisions. Follow Plan, Approve, Execute: produce a plan first, ask for approval, then implement only after approval. Do not skip planning or approval.

Report completion or the suggested next step.
