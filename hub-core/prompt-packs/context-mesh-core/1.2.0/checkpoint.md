# Prompt: Checkpoint (Quality Gates)

Use this prompt to verify quality gates before phase transitions.

**What are quality gates?** Checkpoints that ensure requirements are met before proceeding. Context Mesh has gates at each transition:
- **Intent → Build**: Feature complete, ADR exists, no validation errors
- **Build → Learn**: Implementation complete, tests pass, AC met

## How to Use

1. **Copy** the prompt below
2. **Paste** in your AI assistant (Cursor, Copilot, Claude, etc.)
3. **Review** gate results
4. **Fix** any blockers
5. **Proceed** when gate passes

---

## Prompt: Intent → Build Gate

```
Check the Intent → Build quality gate.

**FIRST: Load context:**
- Load @context/.context-mesh-framework.md (if exists)
- Load @context/intent/feature-[name].md
- Load @context/decisions/*.md (relevant decisions)

**CHECK each gate criterion:**

## Gate 1: Intent Clarity
- [ ] Feature has ## What section (descriptive, not vague)
- [ ] Feature has ## Why section (business value clear)
- [ ] Feature has Acceptance Criteria (measurable, testable)
- [ ] Feature has ## Status section

## Gate 2: Technical Decision (ADR)
- [ ] Decision file exists for this feature
- [ ] Decision has ## Context (situation, constraints)
- [ ] Decision has ## Decision (chosen approach)
- [ ] Decision has ## Rationale (why this approach)
- [ ] Decision has ## Alternatives Considered
- [ ] Decision links back to feature (bidirectional)

## Gate 3: Context Integrity
- [ ] No validation errors in context/
- [ ] Bidirectional links are correct
- [ ] Status sections are up-to-date

**OUTPUT FORMAT:**

```
## Intent → Build Gate: [FEATURE_NAME]

### Results
- Intent Clarity: [PASS/FAIL] ([X/Y] checks)
- Technical Decision: [PASS/FAIL] ([X/Y] checks)
- Context Integrity: [PASS/FAIL] ([X/Y] checks)

### Blockers (if any)
- [ ] [Specific blocker with action to fix]

### Overall: [PASS/BLOCKED]

### Recommendation
[If PASS]: Ready to create build plan. Use build_plan() or execute section of add-feature.md
[If BLOCKED]: Address blockers before proceeding.
```

Ask me which feature to check.
```

---

## Prompt: Build → Learn Gate

```
Check the Build → Learn quality gate.

**FIRST: Load context:**
- Load @context/.context-mesh-framework.md (if exists)
- Load @context/intent/feature-[name].md
- Load @context/decisions/*.md (relevant decisions)
- Analyze the codebase for implementation status

**CHECK each gate criterion:**

## Gate 1: Implementation Complete
- [ ] All files from build plan exist
- [ ] Code compiles/runs without errors
- [ ] No TODO comments indicating incomplete work

## Gate 2: Acceptance Criteria Met
- [ ] Each acceptance criterion from feature intent verified
- [ ] Edge cases handled (based on clarify questions)
- [ ] Error handling in place

## Gate 3: Tests (if applicable)
- [ ] Unit tests exist and pass
- [ ] Integration tests exist and pass (if required)
- [ ] No regressions introduced

## Gate 4: Ready for Learn
- [ ] Feature status can be updated to "Completed" or needs refinement
- [ ] Outcomes can be documented
- [ ] Learnings are identifiable

**OUTPUT FORMAT:**

```
## Build → Learn Gate: [FEATURE_NAME]

### Results
- Implementation Complete: [PASS/FAIL] ([X/Y] checks)
- Acceptance Criteria Met: [PASS/FAIL] ([X/Y] checks)
- Tests: [PASS/FAIL/N/A] ([X/Y] checks)
- Ready for Learn: [PASS/FAIL] ([X/Y] checks)

### Blockers (if any)
- [ ] [Specific blocker with action to fix]

### Overall: [PASS/BLOCKED]

### Recommendation
[If PASS]: Ready to sync learnings. Use learn-update.md or learn_sync_initiate()
[If BLOCKED]: Complete implementation before syncing learnings.
```

Ask me which feature to check.
```

---

## Quick Gate Check

For a quick check without detailed analysis:

```
Quick quality gate check for [feature-name].

Check:
1. Does feature-[name].md exist and have What, Why, AC?
2. Does a related decision file exist?
3. Are there validation errors in context/?

Tell me: PASS (ready to build) or BLOCKED (with reason).
```

---

## What This Prompt Does

- **Verifies prerequisites** before phase transitions
- **Prevents premature progress** with incomplete context
- **Identifies specific blockers** with actionable fixes
- **Enforces Context Mesh governance** (ADR before implementation)

**Key Insight**: Gates prevent expensive mistakes. A missing ADR caught now saves hours of rework later.

---

## Quality Gate Summary

| Gate | Checks | Required For |
|------|--------|--------------|
| Intent → Build | Feature complete, ADR exists, no errors | Starting implementation |
| Build → Learn | Implementation done, AC met, tests pass | Syncing learnings |

---

## Related Prompts

- **Before this**: `clarify.md` (reduce ambiguity)
- **After Intent→Build**: Execute section of `add-feature.md`
- **After Build→Learn**: `learn-update.md` or `retrospective.md`
