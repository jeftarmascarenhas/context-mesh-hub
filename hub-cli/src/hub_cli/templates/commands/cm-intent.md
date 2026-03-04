---
description: Run Intent phase actions — new project, add feature, fix bug, create decision (Context Mesh).
handoffs:
  - label: Add feature
    agent: cm-add-feature
    prompt: Add a new feature to the Context Mesh.
  - label: New project
    agent: cm-new-project
    prompt: Initialize a new Context Mesh project.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/cm-intent` is the intent (e.g. "add feature for login", "new project") — use it.

**If Context Mesh Hub MCP is available:** Choose the right action from the user's message and call the appropriate tool:

- New project / init → `cm_init(action="new")`
- Existing project → `cm_init(action="existing")`
- Add feature → `cm_intent(action="create", type="feature", name="<name>", ...)`
- Fix bug → `cm_intent(action="create", type="bug", name="<name>", ...)`
- Create decision (ADR) → `cm_intent(action="create", type="decision", ...)`
- List features → `cm_intent(action="list", type="feature")`
- Get feature → `cm_intent(action="get", type="feature", name="<name>")`

If unclear, call `cm_status()` and suggest an action.

**If MCP is not available:** Load @context/.context-mesh-framework.md and @context/intent/project-intent.md. Interpret intent: new project (create context/), add feature (feature + decision files), fix bug (bug intent), or create ADR (decision file). Follow Context Mesh file structure and bidirectional links.

Report completion or the suggested next step.

## MCP Tool Reference (D013 Consolidated)

| Old Tool | New Tool Call |
|----------|---------------|
| cm_new_project | cm_init(action="new") |
| cm_existing_project | cm_init(action="existing") |
| cm_add_feature | cm_intent(action="create", type="feature") |
| cm_update_feature | cm_intent(action="update", type="feature") |
| cm_fix_bug | cm_intent(action="create", type="bug") |
| cm_create_decision | cm_intent(action="create", type="decision") |
| cm_list_features | cm_intent(action="list", type="feature") |
| cm_help | cm_status() |
| cm_status | cm_status() |
