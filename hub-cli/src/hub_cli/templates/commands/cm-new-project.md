---
description: Initialize a new Context Mesh project (create context/ structure in this repo).
handoffs:
  - label: Add feature
    agent: cm-add-feature
    prompt: Add the first feature to the project.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/cm-new-project` is optional project description — use it if present.

**If Context Mesh Hub MCP is available:** Call the MCP tool `cm_new_project` (for full setup) or `cm_init` (for minimal setup). If the user gave details (project name, description), pass them; otherwise the tool or you can ask.

**If MCP is not available:** Load @context/.context-mesh-framework.md. Create context/ with: intent/project-intent.md, decisions/, knowledge/patterns/, knowledge/anti-patterns/, agents/, evolution/changelog.md, and .context-mesh-framework.md. Ask for project name, what it does, and why, then fill project-intent.md.

Report completion with the context path and suggested next step (e.g. `/cm-add-feature`).
