---
description: Show current Context Mesh project status (phase, artifacts, validation, next step).
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**If Context Mesh Hub MCP is available:** Call the MCP tool:

```
cm_status()
```

Present the result: project phase, artifacts count, validation state, and next step suggestion.

**If MCP is not available:** Load @context/ and summarize: project intent present, number of features and decisions, validation state (e.g. from context/.context-mesh-framework.md and context/intent/). Suggest next step (add feature, create plan, sync learnings).

Present the status clearly and suggest the next command (e.g. `/cm-add-feature`, `/cm-build-plan`, `/cm-sync-learn`).

## MCP Tool Reference (D013 Consolidated)

| Old Tool | New Tool Call |
|----------|---------------|
| cm_status | cm_status() |
| hub_health | cm_status() |
| cm_lifecycle_state | cm_status() |
| cm_suggest_next | cm_status() |
| cm_workflow_guide | cm_status() |
