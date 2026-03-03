# Prompt: Clarify Feature

Use this prompt **before building** to ensure a feature is well-understood and reduce ambiguity.

**Why clarify?** Starting implementation with unclear requirements leads to rework. This prompt generates targeted questions to identify gaps, ambiguities, and missing details in the feature intent.

## How to Use

1. **Copy** the prompt below
2. **Paste** in your AI assistant (Cursor, Copilot, Claude, etc.)
3. **Review** the generated questions
4. **Answer** or update the feature intent
5. **Build** once all critical questions are resolved

---

## Prompt

```
Clarify a feature before building to reduce ambiguity.

**FIRST: Load context:**
- Load @context/.context-mesh-framework.md (if exists)
- Load @context/intent/feature-[name].md (the feature to clarify)
- Load @context/decisions/[related-decision].md (if exists)

**ANALYZE the feature for completeness:**

Check each section:
1. **What section** - Is it specific enough? Can someone unfamiliar understand what will be built?
2. **Why section** - Is the business/user value clear? Why does this matter?
3. **Acceptance Criteria** - Are they measurable? Testable? Complete?
4. **Technical Decision** - Does an ADR exist? Is the approach documented?

**GENERATE clarifying questions:**

For each gap or ambiguity found, generate a specific question:

**Completeness Questions:**
- If What is vague: "What exactly does [X] mean? Can you provide an example?"
- If Why is missing: "Why is this feature important? Who benefits and how?"
- If AC is incomplete: "How will we know when [criterion] is satisfied? What's the success metric?"

**Scope Questions:**
- "What is explicitly OUT of scope for this feature?"
- "What is the minimum viable version of this feature?"
- "What can be deferred to a later iteration?"

**Technical Questions:**
- "Does this feature have dependencies on other features or systems?"
- "Are there constraints (performance, security, compatibility) to consider?"
- "What existing patterns or code can be reused?"

**Edge Cases:**
- "What happens if [edge case]?"
- "How should the system behave when [error condition]?"
- "What are the limits or boundaries (max users, max size, etc.)?"

**User Experience:**
- "Who is the primary user of this feature?"
- "What is the user's workflow/journey?"
- "What feedback does the user receive?"

**OUTPUT FORMAT:**

1. **Completeness Score**: X% (based on sections present and detailed)
2. **Critical Questions** (must answer before building): [list]
3. **Recommended Questions** (should answer): [list]
4. **Nice-to-Have Questions** (can answer during build): [list]

**RECOMMENDATION:**
- If Completeness Score < 75%: "Address critical questions before building"
- If Completeness Score >= 75%: "Ready to build. Consider recommended questions for thoroughness"

Ask me which feature to clarify.
```

---

## Example Output

```
Feature: user-authentication
Completeness Score: 60%

## Critical Questions (Must Answer)
1. What authentication methods are supported? (email/password, OAuth, magic link?)
2. What happens when a user fails authentication 3 times? (lockout? captcha?)
3. How long should sessions last before requiring re-authentication?

## Recommended Questions (Should Answer)
1. Is MFA (multi-factor authentication) in scope for v1?
2. How should "remember me" functionality work?
3. What password requirements exist? (length, complexity)

## Nice-to-Have Questions (Can Answer During Build)
1. What should the error messages say?
2. Should we track failed login attempts?

RECOMMENDATION: Address critical questions before building.
```

---

## After Clarification

Once questions are answered:

1. **Update the feature intent** with new information
2. **Create/update the ADR** if technical decisions were made
3. **Proceed to build**: Use `add-feature.md` execute section or `build-plan`

---

## What This Prompt Does

- **Analyzes** feature completeness systematically
- **Identifies gaps** in What, Why, Acceptance Criteria, and Technical Decision
- **Generates targeted questions** to reduce ambiguity
- **Prioritizes questions** by criticality
- **Gives recommendation** on whether to proceed or clarify first

**Key Insight**: Time spent clarifying saves 10x the time in rework.

---

## Related Prompts

- **Before this**: `add-feature.md` (create the feature first)
- **After this**: `checkpoint.md` (verify quality gates before building)
- **Alternative**: `build-plan` MCP tool for automated analysis
