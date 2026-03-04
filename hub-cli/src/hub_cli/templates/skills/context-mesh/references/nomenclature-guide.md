# Nomenclature Guide: Naming Patterns and Templates

This guide covers the naming conventions and YAML frontmatter templates for Context Mesh artifacts.

---

## Naming Patterns

### Features: F001, F002, ...

Features use the pattern: `F{NNN}-{slug}.md`

- `F` = Feature prefix
- `NNN` = Zero-padded sequential number (001, 002, ...)
- `slug` = Kebab-case descriptive name

**Examples:**
```
F001-user-auth.md
F002-payment-processing.md
F003-email-notifications.md
F010-admin-dashboard.md
```

### Decisions: D001, D002, ...

Decisions (ADRs) use the pattern: `D{NNN}-{slug}.md`

- `D` = Decision prefix
- `NNN` = Zero-padded sequential number
- `slug` = Kebab-case descriptive name

**Examples:**
```
D001-tech-stack.md
D002-auth-strategy.md
D003-database-schema.md
D004-api-versioning.md
```

### Bugs: B001, B002, ... (Optional)

Bugs use the pattern: `B{NNN}-{slug}.md`

- `B` = Bug prefix
- `NNN` = Zero-padded sequential number
- `slug` = Kebab-case descriptive name

**Examples:**
```
B001-login-timeout.md
B002-payment-double-charge.md
B003-email-not-sending.md
```

### Agents: A001, A002, ...

Agents use the pattern: `A{NNN}-{role}.md` or `agent-{role}.md`

**Examples:**
```
A001-backend.md
A002-frontend.md
agent-backend.md
agent-qa.md
```

### Learnings: L001, L002, ... (Internal)

Learnings (for Learn Sync) use the pattern: `L{NNN}`

**Examples:**
```
L001 - JWT refresh needed more client work
L002 - Rate limiting prevented abuse
```

---

## YAML Frontmatter Templates

### Feature Template

```yaml
---
id: F001
type: feature
title: User Authentication
status: draft | ready | in-progress | completed | blocked | cancelled
priority: high | medium | low
created: 2024-01-15
updated: 2024-01-20
depends_on: []           # e.g., [F002, F003]
decisions: [D001, D002]  # Related decisions
agents: [A001-backend]   # Optional
---
```

### Decision Template

```yaml
---
id: D001
type: decision
title: Tech Stack Selection
status: proposed | accepted | superseded | deprecated
created: 2024-01-10
updated: 2024-01-12
features: [F001, F002]   # Features this applies to
supersedes: null         # e.g., D000 if replacing old decision
superseded_by: null      # Set when this is superseded
related: [D002, D003]    # Related decisions
---
```

### Bug Template

```yaml
---
id: B001
type: bug
title: Login Timeout on Slow Networks
status: reported | confirmed | in-progress | fixed | wont-fix
severity: critical | high | medium | low
created: 2024-01-18
updated: 2024-01-19
features: [F001]         # Affected features
decisions: []            # Decisions to create/update
---
```

### Agent Template

```yaml
---
id: A001
name: backend
type: agent
description: Backend development agent
created: 2024-01-10
updated: 2024-01-15
features: [F001, F002]   # Features this agent works on
---
```

---

## Full File Examples

### Feature Example

```markdown
---
id: F001
type: feature
title: User Authentication
status: draft
priority: high
created: 2024-01-15
updated: 2024-01-20
depends_on: []
decisions: [D001, D002]
agents: [A001-backend]
---

# Feature: User Authentication

## What

Implement secure user authentication with email/password and OAuth providers.

## Why

**Business Value**
- Users need secure access to their accounts
- OAuth reduces friction for registration

**Technical Value**
- Foundation for all user-specific features
- Centralized auth enables single sign-on later

## Acceptance Criteria

- [ ] Users can register with email/password
- [ ] Users can login with email/password
- [ ] Users can login with Google OAuth
- [ ] Sessions expire after 24 hours
- [ ] Failed login attempts are rate-limited (5 per minute)
- [ ] Users can reset their password via email

## Constraints

- Must use existing user database schema
- OAuth must support Google initially, expandable to GitHub/Apple
- Must comply with GDPR for EU users

## Related

- [D001: Tech Stack](../decisions/D001-tech-stack.md)
- [D002: Auth Strategy](../decisions/D002-auth-strategy.md)
```

### Decision Example

```markdown
---
id: D001
type: decision
title: Authentication Strategy
status: accepted
created: 2024-01-10
updated: 2024-01-12
features: [F001]
supersedes: null
superseded_by: null
related: [D002]
---

# Decision: Authentication Strategy

## Context

We need to authenticate users for the application. The system will eventually 
support multiple services, so the auth approach needs to be scalable.

## Options Considered

### Option A: Session-based Authentication
- ✅ Simple to implement
- ✅ Well-understood pattern
- ❌ Harder to scale across multiple services
- ❌ Requires session storage (Redis, database)

### Option B: JWT Tokens (Selected)
- ✅ Stateless - no server-side session storage
- ✅ Works well with microservices
- ✅ Can include claims for authorization
- ❌ Token revocation is complex
- ❌ Larger payload than session cookies

### Option C: OAuth2 Only (External)
- ✅ No password management
- ❌ Dependency on external providers
- ❌ Not all users have OAuth accounts

## Decision

Use **JWT tokens** for authentication with the following configuration:
- Access tokens: 1-hour expiry
- Refresh tokens: 7-day expiry, stored securely
- Support both email/password and OAuth as login methods

## Consequences

### Positive
- Scalable to multiple services
- No session storage required
- Works with mobile apps and SPAs

### Negative
- Need to implement token refresh flow on client
- Token revocation requires additional mechanism (blacklist)
- Slightly larger request headers

## Outcomes (Post-Implementation)

*Added during Learn phase:*
- Token refresh worked well on web
- Mobile needed extra handling for background refresh
- Consider adding token revocation for admin use cases
```

### Bug Example

```markdown
---
id: B001
type: bug
title: Login Timeout on Slow Networks
status: confirmed
severity: high
created: 2024-01-18
updated: 2024-01-19
features: [F001]
decisions: []
---

# Bug: Login Timeout on Slow Networks

## Description

Users on slow networks (3G, high latency) experience timeout errors 
during login, even with valid credentials.

## Steps to Reproduce

1. Throttle network to 3G (Chrome DevTools)
2. Navigate to login page
3. Enter valid credentials
4. Click "Login"
5. Wait 10 seconds
6. See timeout error

## Expected Behavior

Login should complete successfully or show meaningful error.

## Actual Behavior

Generic "Request timed out" error after 10 seconds.

## Root Cause

*To be determined during investigation*

## Proposed Fix

Increase timeout to 30 seconds for auth endpoints and add retry logic.

## Acceptance Criteria

- [ ] Login works on 3G networks
- [ ] Meaningful error if request fails after retries
- [ ] No change for users on fast networks
```

---

## Status Values

### Feature Statuses

| Status | Description |
|--------|-------------|
| `draft` | Initial capture, may be incomplete |
| `ready` | Complete and ready for implementation |
| `in-progress` | Currently being built |
| `completed` | Implementation finished |
| `blocked` | Waiting on dependency |
| `cancelled` | Will not be implemented |

### Decision Statuses

| Status | Description |
|--------|-------------|
| `proposed` | Under consideration |
| `accepted` | Approved and in use |
| `superseded` | Replaced by newer decision |
| `deprecated` | Still in use but discouraged |

### Bug Statuses

| Status | Description |
|--------|-------------|
| `reported` | Newly reported, unverified |
| `confirmed` | Verified as real issue |
| `in-progress` | Being worked on |
| `fixed` | Fix implemented |
| `wont-fix` | Decided not to fix |

---

## File Location

```
context/
├── intent/
│   ├── project-intent.md    # No prefix
│   ├── F001-user-auth.md
│   ├── F002-payment.md
│   └── B001-login-timeout.md
│
├── decisions/
│   ├── D001-tech-stack.md
│   ├── D002-auth-strategy.md
│   └── D003-database.md
│
├── agents/
│   ├── A001-backend.md
│   └── A002-frontend.md
│
├── knowledge/
│   ├── patterns/
│   │   └── README.md
│   └── anti-patterns/
│       └── README.md
│
└── evolution/
    ├── changelog.md
    └── archived/
```

---

## Best Practices

1. **Use sequential numbering** — Don't skip numbers, even if items are deleted
2. **Keep slugs descriptive** — `F001-user-auth.md` not `F001-feat1.md`
3. **Update timestamps** — Always update `updated:` when modifying
4. **Link related items** — Use `depends_on`, `decisions`, `features` fields
5. **Validate after changes** — Run `cm_validate()` to check consistency
