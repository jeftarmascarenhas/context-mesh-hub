---
description: Show current Context Mesh project status (phase, artifacts, validation, next step).
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**If Context Mesh Hub MCP is available:** Call the MCP tool `cm_status` and present the result (project phase, artifacts count, validation, next step). Optionally call `cm_suggest_next` for a concrete next action.

**If MCP is not available:** Load @context/ and summarize: project intent present, number of features and decisions, validation state (e.g. from context/.context-mesh-framework.md and context/intent/). Suggest next step (add feature, create plan, sync learnings).

Present the status clearly and suggest the next command (e.g. `/cm-add-feature`, `/cm-build-plan`, `/cm-sync-learn`).
