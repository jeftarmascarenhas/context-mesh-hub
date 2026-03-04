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

**If Context Mesh Hub MCP is available:** Choose the right action from the user's message and call `cm_learn`:

- Sync learnings → `cm_learn(action="initiate", feature_name="<name>", user_feedback="...")`
- Review proposal → `cm_learn(action="review", proposal_id="<id>")`
- Accept learnings → `cm_learn(action="accept", proposal_id="<id>")`
- Apply learnings → `cm_learn(action="apply", proposal_id="<id>")`

If unclear, call `cm_learn(action="initiate", ...)` for the feature they just implemented and guide them through review/apply.

**If MCP is not available:** Load @context/.context-mesh-framework.md and the feature intent. Ask what was implemented, what worked, what was hard. Propose updates to decision Outcomes, patterns, and changelog. Update context/evolution/changelog.md and decision files.

Report completion or the suggested next step.

## MCP Tool Reference (D013 Consolidated)

| Old Tool | New Tool Call |
|----------|---------------|
| learn_sync_initiate | cm_learn(action="initiate") |
| learn_sync_review | cm_learn(action="review") |
| learn_sync_accept | cm_learn(action="accept") |
| learn_sync_apply | cm_learn(action="apply") |
