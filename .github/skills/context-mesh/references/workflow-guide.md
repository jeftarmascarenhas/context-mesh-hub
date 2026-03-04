# Workflow Guide: Intent → Build → Learn

This guide provides detailed instructions for each phase of the Context Mesh workflow.

---

## Phase 1: Intent

**Purpose**: Define what to build and why before writing any code.

### What to Capture

Every intent artifact should answer:

1. **What** — Clear description of the feature/change
2. **Why** — Business and technical value
3. **Acceptance Criteria** — How to know when it's done
4. **Constraints** — Limitations and boundaries
5. **Dependencies** — Related features and decisions

### Creating a Feature Intent

```markdown
---
id: F001
type: feature
title: User Authentication
status: draft
priority: high
created: 2024-01-15
depends_on: []
decisions: [D001, D002]
---

# Feature: User Authentication

## What
Implement secure user authentication with email/password and OAuth.

## Why
- **Business**: Users need secure access to their accounts
- **Technical**: Foundation for all user-specific features

## Acceptance Criteria
- [ ] Users can register with email/password
- [ ] Users can login with email/password
- [ ] Users can login with Google OAuth
- [ ] Sessions expire after 24 hours
- [ ] Failed login attempts are rate-limited

## Constraints
- Must use existing user database schema
- OAuth must support Google initially, expandable later
```

### Creating a Decision (ADR)

Decisions should be created **before** implementation. They capture:
- The context that led to the decision
- Options considered and trade-offs
- The chosen approach and rationale

```markdown
---
id: D001
type: decision
title: Authentication Strategy
status: accepted
created: 2024-01-10
features: [F001]
---

# Decision: Authentication Strategy

## Context
We need to authenticate users securely while supporting multiple auth methods.

## Options Considered

### Option A: Session-based auth
- ✅ Simple to implement
- ❌ Harder to scale across services

### Option B: JWT tokens (Selected)
- ✅ Stateless, scalable
- ✅ Works with microservices
- ❌ Token revocation complexity

## Decision
Use JWT tokens with short expiry (1 hour) and refresh tokens.

## Consequences
- Need to implement token refresh flow
- Need secure token storage on client
```

### Intent Statuses

| Status | Meaning |
|--------|---------|
| `draft` | Initial capture, may be incomplete |
| `ready` | Complete and ready for implementation |
| `in-progress` | Currently being built |
| `completed` | Implementation finished |
| `blocked` | Waiting on dependency |
| `cancelled` | Will not be implemented |

---

## Phase 2: Build

**Purpose**: AI generates code using context, human supervises.

### The Plan → Approve → Execute Flow

#### Step 1: Plan

Before writing any code, ask the AI to explain what it will build:

```
Create a plan for implementing F001 (User Authentication).
Load the context from @context/intent/F001-user-auth.md and @context/decisions/D001-auth-strategy.md
```

The AI should produce:
- List of files to create/modify
- Order of operations
- Technical approach
- Potential risks

#### Step 2: Approve

Review the plan carefully:
- Does it align with the intent?
- Does it follow the decision?
- Are there any concerns?

Only proceed after explicit approval: "This plan looks good. Proceed."

#### Step 3: Execute

With approval, the AI generates code. During execution:
- Follow established patterns
- Reference decisions for guidance
- Ask for clarification if unsure

### Verify Decision Before Building

**Critical**: Before implementing any feature, verify a decision exists.

```
Check: Does a decision exist for the technical approach?

If NO → Create the decision first (go back to Intent phase)
If YES → Proceed with planning
```

### Context Bundling

Use `cm_build(operation="bundle")` to gather all relevant context:

```
cm_build(operation="bundle", feature_id="F001")
```

This collects:
- Feature intent
- Related decisions
- Relevant patterns
- Anti-patterns to avoid

### Update vs. New Implementation

When updating existing features:
1. Analyze existing code first
2. Make incremental changes only
3. Preserve code that doesn't need to change
4. Follow "Changes from Original" if present in intent

---

## Phase 3: Learn

**Purpose**: Update context to reflect what actually happened.

### When to Trigger Learn

Learn should be triggered:
- After completing a build cycle
- After failed or reverted changes
- When unexpected side effects occur
- When requirements become clearer

### What to Capture

#### Evolution Entries
What changed and why:
```markdown
## 2024-01-20: F001 User Authentication

- Implemented JWT authentication
- Added refresh token flow
- Integrated Google OAuth
- Decision D001 confirmed as appropriate
```

#### Decision Outcomes
Update decisions with actual results:
```markdown
## Outcomes (added during Learn)
- JWT approach worked well for our scale
- Token refresh required more client complexity than expected
- Consider adding token revocation for admin use cases
```

#### Pattern Recognition
If you discovered a reusable approach:
```markdown
# Pattern: Token Refresh Flow

## Context
When using short-lived JWT tokens with refresh tokens.

## Solution
Implement client-side interceptor that:
1. Detects 401 responses
2. Attempts token refresh
3. Retries original request
4. Logs out if refresh fails
```

### Learn Sync Workflow

```
1. cm_learn(operation="initiate", feature_id="F001")
   → AI proposes learnings based on what changed

2. cm_learn(operation="review")
   → Review proposed learnings

3. cm_learn(operation="accept", learning_ids=["L001"])
   → Accept relevant learnings

4. cm_learn(operation="apply")
   → Apply accepted learnings to context
```

### Update Feature Status

After completing work:
```
cm_intent(operation="update", type="feature", id="F001", status="completed")
```

### Validate Everything

After Learn phase, always validate:
```
cm_validate()
```

This ensures:
- All links between artifacts are valid
- Statuses are consistent
- No orphaned references

---

## Feedback Loop

The Learn phase feeds back into Intent:
- Learnings refine understanding for future features
- Patterns inform future decisions
- Anti-patterns prevent repeated mistakes

```
Intent → Build → Learn
                   │
    ◄──────────────┘
    Refined understanding
```

---

## Tips for Effective Workflow

### Keep Intent Concise
- Focus on what and why
- Don't include implementation details
- Let decisions capture the how

### Make Decisions Early
- Create decisions before building
- It's okay to start with "proposed" status
- Update to "accepted" when validated

### Learn Continuously
- Don't wait until the end
- Capture learnings as they happen
- Small, frequent updates are better than one big dump

### Validate Often
- Run `cm_validate()` after changes
- Fix issues immediately
- Keep context healthy
