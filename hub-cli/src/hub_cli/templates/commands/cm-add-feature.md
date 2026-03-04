---
description: Add a new feature to the Context Mesh (Intent phase). Define what to build and why.
handoffs:
  - label: Build plan
    agent: cm-build-plan
    prompt: Create an implementation plan for this feature.
  - label: Clarify feature
    agent: cm-clarify
    prompt: Clarify underspecified areas in the feature intent.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/cm-add-feature` in the triggering message **is** the feature description or name. Assume you always have it available in this conversation. Do not ask the user to repeat it unless they provided an empty command.

**If Context Mesh Hub MCP is available:** Call the MCP tool:

```
cm_intent(action="create", type="feature", name="<feature-name>", what="<description>", why="<rationale>", acceptance_criteria=[...])
```

If the user only said "add a feature" or gave a short description, ask for: feature name, what it does, why we need it, and acceptance criteria, then call the tool.

**If MCP is not available:** Load @context/.context-mesh-framework.md and @context/intent/project-intent.md. Then:
1. Check if the feature already exists in context/intent/ (F###-[name].md). If it exists, say so and suggest update-feature or a different name.
2. Ask for: feature name, what it does, why we need it, acceptance criteria, and technical decision (approach, rationale, alternatives).
3. Create context/intent/F###-[name].md and context/decisions/D###-[name].md with bidirectional links. Update project-intent.md Related section and changelog.

Report completion with the feature file path and suggested next step (e.g. `/cm-build-plan` or `/cm-clarify`).

## MCP Tool Reference (D013 Consolidated)

| Old Tool | New Tool Call |
|----------|---------------|
| cm_add_feature | cm_intent(action="create", type="feature") |
| cm_update_feature | cm_intent(action="update", type="feature") |
| cm_list_features | cm_intent(action="list", type="feature") |
