---
id: D013
type: decision
title: MCP Simplification - 43 to 8 Tools
status: accepted
created: 2026-03-03
updated: 2026-03-03
features: [F-hub-core]
supersedes: null
superseded_by: null
related: [D002, D003, D010]
---

# D013: MCP Simplification - 43 to 8 Tools

## Context

The Context Mesh Hub MCP server has grown to 43 tools, creating:
- **Cognitive overload** for AI agents choosing tools
- **Redundancy** between similar tools (e.g., `cm_add_feature` vs `intent_add_feature`)
- **Complexity** that contradicts Context Mesh's philosophy: "The intelligence is in the Skill, not the MCP"

Context Mesh is a **documentation framework**, not a complex orchestration system. The MCP should be **CRUD + optimized reading**, with intelligence coming from Skills.

## Decision

### 1. Consolidate 43 Tools → 8 Tools

| Tool | Description | Consolidates | Operations |
|------|-------------|--------------|------------|
| `cm_init` | Initialize/migrate `context/` structure | cm_new_project, cm_existing_project, cm_init | `init`, `migrate`, `existing` |
| `cm_intent` | CRUD for features and decisions | cm_add_feature, cm_fix_bug, cm_create_decision, cm_update_feature, cm_list_*, context_read | `create`, `update`, `get`, `list`, `delete` for `feature` and `decision` |
| `cm_agent` | Manage agent files | cm_create_agent, intent_create_agent | `create`, `update`, `get`, `list`, `delete` |
| `cm_build` | Bundle + Build Protocol | context_bundle, build_plan, build_approve, build_execute | `bundle`, `plan`, `approve`, `execute` |
| `cm_validate` | Validate consistency | context_validate | Structure, links, status |
| `cm_analyze` | Impact analysis and dependencies | brownfield_scan, brownfield_slice, brownfield_extract, brownfield_report | `scan`, `impact`, `dependencies`, `graph` |
| `cm_learn` | Learn Sync | learn_sync_initiate, learn_sync_review, learn_sync_accept, learn_sync_apply | `initiate`, `review`, `accept`, `apply` |
| `cm_status` | Complete context status | hub_health, cm_status, cm_lifecycle_state, cm_suggest_next, cm_workflow_guide | Overview, lifecycle, suggestions |

### 2. Implement MCP Resources

Expose context without consuming tokens:

| URI | Description |
|-----|-------------|
| `context://intent/` | List features (F001, F002...) |
| `context://decisions/` | List decisions (D001, D002...) |
| `context://agents/` | List agents |
| `context://knowledge/` | List patterns/anti-patterns |

### 3. Implement MCP Prompts

Reusable templates:

| Prompt | Purpose |
|--------|---------|
| `new-feature` | Template for creating feature |
| `new-decision` | Template for creating decision |
| `analyze-project` | Brownfield instructions |

### 4. Standardized Nomenclature

```
context/
├── intent/
│   ├── project-intent.md
│   ├── F001-user-auth.md          # Feature 001
│   ├── F002-payment.md            # Feature 002
│   └── B001-login-error.md        # Bug 001 (optional)
├── decisions/
│   ├── D001-tech-stack.md
│   ├── D002-auth-approach.md
│   └── D003-database-schema.md
└── ...
```

### 5. Templates with YAML Frontmatter

**Feature Template:**
```yaml
---
id: F001
type: feature
title: User Authentication
status: draft | in-progress | completed | blocked
priority: high | medium | low
created: 2024-01-15
updated: 2024-01-20
depends_on: []
decisions: [D001, D002]
agents: [A001-backend]
---
```

**Decision Template:**
```yaml
---
id: D001
type: decision
title: Tech Stack Selection
status: proposed | accepted | superseded | deprecated
created: 2024-01-10
updated: 2024-01-12
features: [F001, F002]
supersedes: null
superseded_by: null
---
```

### 6. Context Mesh Skill

Create a Skill that instructs AI on:
- Intent → Build → Learn workflow
- When to use each consolidated tool
- How to do brownfield (via analysis, not dedicated tools)
- Optional parallelization with sub-agents

## Alternatives Considered

### Option A: Keep 43 Tools (Status Quo)
- ✅ No migration needed
- ❌ Cognitive overload for agents
- ❌ Redundancy and confusion
- ❌ Contradicts "simple MCP" philosophy

### Option B: Extreme Reduction (3-4 Tools)
- ✅ Maximum simplicity
- ❌ Too much logic in single tool parameters
- ❌ Poor discoverability
- ❌ Complex parameter schemas

### Option C: 8 Consolidated Tools (Selected)
- ✅ Clear separation by domain (intent, build, learn)
- ✅ Follows Intent → Build → Learn workflow
- ✅ Good balance of simplicity and discoverability
- ✅ Intelligence moves to Skill layer

## Consequences

### Positive
1. **Simpler mental model**: 8 tools aligned with workflow
2. **Better agent performance**: Less choice paralysis
3. **Clear responsibility**: MCP is CRUD, Skill is intelligence
4. **Easier maintenance**: Less code duplication

### Negative
1. **Breaking change**: Existing integrations need updates
2. **Migration effort**: CLI, slash commands, documentation
3. **Learning curve**: Users need to learn new tool names

### Mitigations
1. **Aliases**: Keep old tool names as deprecated aliases for 2 versions
2. **Migration tool**: `cm_init --migrate` for automatic conversion
3. **Documentation**: Clear migration guide

## Implementation

### Parallel Streams
- **Stream A**: MCP tool refactoring (hub-core)
- **Stream B**: Skill creation (.github/skills/context-mesh)
- **Stream C**: CLI and slash commands update (hub-cli)

### Tool Annotations (per mcp-builder)
All tools should include:
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false

## References

- [Decision 002: MCP Tool Contracts](./D002-mcp-tool-contracts.md)
- [Decision 003: Context Bundling Strategy](./D003-context-bundling-strategy.md)
- [Decision 010: Prompt Pack Resolution](./D010-prompt-pack-resolution-and-update-model.md)
- [mcp-builder Skill](/.github/skills/mcp-builder/SKILL.md)
- [skill-creator Skill](/.github/skills/skill-creator/SKILL.md)
