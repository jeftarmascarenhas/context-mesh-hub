# Fix Bug

Create a bug fix intent following Context Mesh framework.

## Context
- Bug has been identified
- Need to document bug fix intent
- May require new feature intent or update existing

## Required Inputs
- Bug description
- Impact assessment
- Proposed fix approach
- Related feature (if applicable)

## Steps

1. Determine if bug fix requires:
   - New feature intent (significant change)
   - Update to existing feature
   - Simple fix (may not need intent)
2. If intent needed:
   - Create `context/intent/bug-{name}.md` or update feature
   - Document bug description
   - Document fix approach
   - Link to affected feature
   - Add Acceptance Criteria (bug resolved)
3. Ensure changelog entry

## Output
Bug fix intent or updated feature intent with fix documented.

## Constraints
- Must link to affected feature if applicable
- Must include Acceptance Criteria (bug resolved)
- Must document impact and approach
