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

**If Context Mesh Hub MCP is available:** Choose the right tool from the user's message:
- New project / init → `cm_new_project` or `cm_init`
- Add feature → `cm_add_feature`
- Fix bug → `cm_fix_bug`
- Create decision (ADR) → `cm_create_decision`
- List features → `cm_list_features`
If unclear, call `cm_help` or `cm_status` and suggest an action.

**If MCP is not available:** Load @context/.context-mesh-framework.md and @context/intent/project-intent.md. Interpret intent: new project (create context/), add feature (feature + decision files), fix bug (bug intent), or create ADR (decision file). Follow Context Mesh file structure and bidirectional links.

Report completion or the suggested next step.
