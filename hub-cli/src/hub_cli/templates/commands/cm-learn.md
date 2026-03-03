---
description: Run Learn phase — sync learnings, review proposals, apply updates to context (Context Mesh).
handoffs:
  - label: Sync learnings
    agent: cm-sync-learn
    prompt: Initiate learn sync for a feature.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/cm-learn` is optional feature name or summary — use it if present.

**If Context Mesh Hub MCP is available:** Choose the right tool from the user's message:
- Sync learnings → `learn_sync_initiate(feature_name, user_feedback=...)`
- Review proposal → `learn_sync_review(proposal_id)`
- Apply learnings → `learn_sync_apply(proposal_id)`
If unclear, call `learn_sync_initiate` for the feature they just implemented and guide them through review/apply.

**If MCP is not available:** Load @context/.context-mesh-framework.md and the feature intent. Ask what was implemented, what worked, what was hard. Propose updates to decision Outcomes, patterns, and changelog. Update context/evolution/changelog.md and decision files.

Report completion or the suggested next step.
