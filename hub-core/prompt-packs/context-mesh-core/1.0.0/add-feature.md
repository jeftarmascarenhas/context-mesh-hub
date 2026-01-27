# Add Feature

Create a new feature intent following Context Mesh framework.

## Context
- Project intent exists
- Feature is being planned/requested
- Need to create feature intent artifact

## Required Inputs
- Feature name
- What: Description of what the feature does
- Why: Business/user value, problem it solves
- Acceptance Criteria: Functional requirements

## Steps

1. Load project intent
2. Load relevant decisions
3. Create `context/intent/feature-{name}.md` with:
   - What section
   - Why section
   - Acceptance Criteria
   - Related links (project intent, decisions)
   - Status section (Created: date, Status: Draft)
4. Ensure bidirectional links are created

## Output
Generate feature intent file in `context/intent/` following Context Mesh structure.

## Constraints
- Must reference project intent
- Must link to relevant decisions
- Must include Acceptance Criteria
- Must not include implementation details (→ decisions/)
