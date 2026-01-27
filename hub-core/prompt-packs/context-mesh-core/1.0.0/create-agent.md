# Create Agent

Create a new execution agent following Context Mesh framework.

## Context
- Need for new execution agent identified
- Agent should follow Context Mesh agent structure
- Agent must have Definition of Done

## Required Inputs
- Agent name
- Agent purpose
- Execution steps
- Definition of Done criteria
- Context files to load

## Steps

1. Create `context/agents/agent-{name}.md` with:
   - Purpose section
   - Context Files to Load
   - Execution Steps (step-by-step)
   - Definition of Done
   - Scope (what agent can/cannot do)
2. Ensure agent references context files, not duplicates them
3. Link agent to relevant features/decisions

## Output
Agent file in `context/agents/` following Context Mesh agent structure.

## Constraints
- Must reference context, not duplicate
- Must have explicit Definition of Done
- Must not contain feature requirements (→ intent/)
- Must not contain decisions (→ decisions/)
- Must not contain patterns (→ knowledge/)
