---
description: Create an implementation plan for a feature (Build phase: Plan step).
handoffs:
  - label: Build (approve/execute)
    agent: cm-build
    prompt: Approve and execute the plan.
  - label: Gate check
    agent: cm-gate-check
    prompt: Check intent-to-build gate before planning.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/cm-build-plan` is likely the feature name — use it.

**If Context Mesh Hub MCP is available:** Call the MCP tool `build_plan` with the feature name. If the user didn't specify a feature, list features (e.g. via `cm_list_features`) and ask which one, or use the feature they mentioned after the command.

**If MCP is not available:** Load @context/.context-mesh-framework.md, @context/intent/feature-[name].md, and @context/decisions/*.md for that feature. Produce a step-by-step implementation plan: files to create/modify, order of work, constraints from decisions, and acceptance criteria. Do not write code yet — present the plan and ask for approval (Plan, Approve, Execute).

Report completion with the plan summary and suggested next step (e.g. `/cm-build` to approve and execute).
