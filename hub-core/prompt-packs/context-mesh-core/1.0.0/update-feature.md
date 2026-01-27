# Update Feature

Update an existing feature intent.

## Context
- Feature intent already exists
- Feature requirements have changed
- Need to update feature artifact

## Required Inputs
- Feature name (existing)
- Changes to apply (What/Why/Acceptance Criteria updates)

## Steps

1. Load existing feature intent
2. Load project intent and related decisions
3. Update feature intent file:
   - Modify What/Why if needed
   - Update Acceptance Criteria
   - Add/update Related links
   - Update Status section (Updated: date, reason)
4. Ensure changes are documented in changelog

## Output
Updated feature intent file with changes clearly marked.

## Constraints
- Preserve original What/Why unless explicitly superseding
- All changes must be recorded in changelog
- Status updates must be explicit
- Must not remove historical content
