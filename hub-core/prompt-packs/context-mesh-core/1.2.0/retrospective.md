# Prompt: Retrospective

Use this prompt after completing a feature or sprint to capture learnings and improve future work.

**What is a retrospective?** A structured reflection on what went well, what didn't, and what to improve. Context Mesh uses retrospectives to evolve context and capture institutional knowledge.

## How to Use

1. **Copy** the prompt below
2. **Paste** in your AI assistant (Cursor, Copilot, Claude, etc.)
3. **Answer** the reflection questions
4. **Review** generated learnings
5. **Decide** what to add to context

---

## Prompt

```
Run a retrospective for recent work.

**FIRST: Load context:**
- Load @context/.context-mesh-framework.md (if exists)
- Load @context/intent/feature-[name].md (if feature-specific)
- Load @context/decisions/*.md (related decisions)
- Load @context/evolution/changelog.md

**ASK reflection questions:**

## What Went Well? (+)
1. What worked better than expected?
2. What decisions proved to be correct?
3. What patterns were useful?
4. What tools or processes helped?

## What Didn't Go Well? (-)
1. What was harder than expected?
2. What took longer than planned?
3. What decisions needed to be revisited?
4. What blockers slowed progress?

## What Did We Learn? (!)
1. What surprised us?
2. What assumptions were wrong?
3. What constraints did we discover?
4. What would we do differently?

## What Should We Improve? (→)
1. What process changes would help?
2. What patterns should we document?
3. What anti-patterns should we avoid?
4. What should we communicate better?

**AFTER gathering answers, generate:**

## Retrospective Output

### Summary
- Feature/Sprint: [NAME]
- Date: [DATE]
- Participants: [WHO]

### Key Findings

#### Went Well (+)
- [Item 1]
- [Item 2]

#### Challenges (-)
- [Item 1]
- [Item 2]

#### Learnings (!)
- [Item 1]
- [Item 2]

#### Improvements (→)
- [Item 1]
- [Item 2]

### Proposed Context Updates

Based on this retrospective, I recommend:

1. **Update Decision [number]**: Add outcome section with [learning]
2. **Create Pattern**: [pattern-name] - [description]
3. **Create Anti-Pattern**: [anti-pattern-name] - [what to avoid]
4. **Update Changelog**: Record [changes]

### Action Items
- [ ] [Specific action with owner]
- [ ] [Specific action with owner]

Ask me what to retrospect (feature name, sprint, or "recent work").
```

---

## Quick Retrospective

For a shorter retrospective:

```
Quick retrospective for [feature/sprint].

Tell me briefly:
1. What went well? (2-3 things)
2. What was challenging? (2-3 things)
3. What would you do differently? (1-2 things)

I'll help you capture these as context updates.
```

---

## Feature Retrospective Template

For a completed feature:

```
Feature retrospective for [feature-name].

**Load:**
- @context/intent/feature-[name].md
- @context/decisions/[related].md

**Review:**
1. Were all acceptance criteria met? Which were hard?
2. Did the technical approach (ADR) work well?
3. What patterns emerged that should be documented?
4. What should future implementers know?

**Generate:**
- Decision outcome update
- Pattern documentation (if applicable)
- Anti-pattern documentation (if applicable)
- Changelog entry
```

---

## What This Prompt Does

- **Structures reflection** with proven categories (+, -, !, →)
- **Captures learnings** in a format suitable for context updates
- **Proposes concrete updates** to decisions, patterns, changelog
- **Creates action items** for improvement
- **Builds institutional knowledge** over time

**Key Insight**: Every feature is an opportunity to learn. Retrospectives turn experience into reusable context.

---

## Learning Artifact Types

Retrospectives can generate these Context Mesh artifacts:

| Type | When to Create | Location |
|------|---------------|----------|
| Decision Update | Outcome of a decision became clear | `decisions/*.md` Outcomes section |
| Pattern | Reusable approach that worked | `knowledge/patterns/*.md` |
| Anti-Pattern | Approach to avoid | `knowledge/anti-patterns/*.md` |
| Evolution Note | Significant insight | `evolution/learning-*.md` |
| Changelog Entry | What changed | `evolution/changelog.md` |

---

## After Retrospective

1. **Review proposed updates** - Decide which to accept
2. **Apply updates** - Use `learn-update.md` or manually update files
3. **Share learnings** - Ensure team knows about new patterns/anti-patterns
4. **Plan improvements** - Add action items to next sprint/iteration

---

## Related Prompts

- **Before this**: `checkpoint.md` (verify build is complete)
- **Alternative**: `learn-update.md` (automated learning sync)
- **Next**: `add-feature.md` (start next feature with learnings)
