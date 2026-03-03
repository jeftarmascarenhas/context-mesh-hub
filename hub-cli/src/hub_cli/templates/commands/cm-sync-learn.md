---
description: Initiate Learn Sync for a feature — capture what was implemented and propose context updates.
handoffs:
  - label: Learn phase
    agent: cm-learn
    prompt: Review and apply learn sync proposals.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/cm-sync-learn` is optional feature name or summary — use it if present.

**If Context Mesh Hub MCP is available:** Call the MCP tool `learn_sync_initiate` with the feature name and optional user_feedback (what was implemented, what worked, what was hard). If the user didn't specify a feature, ask or use the most recently implemented feature. Then the user can review and apply with learn_sync_review and learn_sync_apply.

**If MCP is not available:** Load @context/.context-mesh-framework.md and @context/intent/feature-[name].md. Ask what was implemented, what worked, what was challenging. Propose updates to decision Outcomes, new patterns/anti-patterns if any, and a changelog entry. Create or update context/evolution/changelog.md and decision Outcomes.

Report completion with the proposal path and suggested next step (e.g. `/cm-learn` to review and apply).
