# Brownfield Guide: Extracting Context from Existing Projects

This guide explains how to adopt Context Mesh in existing codebases without stopping development or rewriting history.

---

## What is Brownfield?

A **brownfield project** is an existing codebase, often with:
- Multiple architectural decisions made over time
- Implicit knowledge not documented anywhere
- Mixed patterns and conventions
- Limited or outdated documentation

Context Mesh helps you **progressively formalize** this implicit knowledge.

---

## Core Principles

### 1. Code is Evidence, Not Intent
- Code reflects past decisions, not current intent
- Intent must be reconstructed explicitly
- Don't trust code alone to tell you "why"

### 2. Progressive Disclosure
- Extract context in layers
- Don't try to document everything at once
- Start with the area you're working on

### 3. Evidence-Based Reasoning
- Claims must reference concrete code locations
- Flag inferences without evidence
- "I think this does X because of Y in file Z"

### 4. Human Validation Required
- All extracted context starts as **proposed**
- Human review before acceptance
- Iterate and refine incrementally

---

## Brownfield Workflow

### Step 1: Initialize

Set up Context Mesh in your existing project:

```
cm_init(operation="existing", project_path="/path/to/project")
```

This creates the `context/` folder structure without modifying your existing code.

### Step 2: Scan

Analyze the repository structure:

```
cm_analyze(operation="scan", path="/path/to/project")
```

The scan produces:
- Directory structure overview
- Detected languages and frameworks
- Entry points and configurations
- Candidate module boundaries

### Step 3: Slice (Optional)

For large codebases, divide into manageable slices:

```
cm_analyze(operation="slice", path="src/auth")
```

Work on one slice at a time. Good slice boundaries:
- Directory boundaries (`src/auth/`, `src/payment/`)
- Logical modules
- Architectural layers (API, domain, data)

### Step 4: Extract Features

From the scan results, propose feature intents:

**What to look for:**
- Directory names that suggest features
- README files or inline comments
- API routes and endpoints
- Main entry points

**Example extraction:**
```
Found: src/auth/
Contains: login.py, register.py, oauth.py, models.py

Proposed Feature F001:
- Title: User Authentication
- Evidence: Directory structure, file names
- Scope: Login, registration, OAuth integration
- Status: proposed
```

### Step 5: Extract Decisions

From code patterns, propose technical decisions:

**What to look for:**
- Framework choices (React, FastAPI, etc.)
- Database patterns (ORM, raw SQL)
- Authentication strategies (JWT, sessions)
- Error handling approaches
- Testing patterns

**Example extraction:**
```
Found: All routes use JWT tokens via @auth decorator
Evidence: src/auth/decorators.py, used in 15 files

Proposed Decision D001:
- Title: JWT Authentication
- Pattern: Decorator-based auth on all protected routes
- Status: proposed
```

### Step 6: Review and Accept

Review each proposed artifact:

```
cm_intent(operation="list", type="feature", status="proposed")
```

For each proposal:
1. Verify the evidence is accurate
2. Refine the description if needed
3. Accept or reject

```
cm_intent(operation="update", type="feature", id="F001", status="draft")
```

---

## Extraction Layers

### Layer 1: Structural Discovery
**Goal**: Understand shape, not meaning.

Look at:
- Directory structure
- Module boundaries
- Entry points
- Build and config files
- Dependency graph

### Layer 2: Intent Reconstruction
**Goal**: Hypothesize intent from usage.

Look at:
- Naming conventions
- Public interfaces
- API routes
- Domain models
- Comments and docstrings

### Layer 3: Decision Inference
**Goal**: Surface technical decisions.

Look at:
- Framework usage patterns
- Persistence strategies
- Integration styles
- Cross-cutting concerns

### Layer 4: Risk Detection
**Goal**: Identify danger zones.

Look at:
- Highly coupled modules
- Low test coverage
- Deprecated patterns
- Critical business paths

---

## Analysis Operations

### Dependency Analysis
Understand how code connects:

```
cm_analyze(operation="dependencies", file_path="src/auth/login.py")
```

Returns:
- What this file imports
- What imports this file
- Circular dependency warnings

### Impact Analysis
Before making changes:

```
cm_analyze(operation="impact", feature_id="F001")
```

Returns:
- Files that would be affected
- Dependent features
- Risk assessment

### Dependency Graph
Visualize relationships:

```
cm_analyze(operation="graph", scope="src/auth")
```

---

## Best Practices

### Start Small
- Pick one feature area to document first
- Don't try to document the entire system
- Expand coverage over time

### Work Backwards from Current Changes
- If you're fixing a bug, document that area
- If you're adding a feature, document related context
- Let current work drive documentation

### Involve Domain Experts
- Code alone can't tell you everything
- Ask people who built it why they made choices
- Capture institutional knowledge

### Accept Incompleteness
- Some context may be lost forever
- Document what you can verify
- Mark uncertain areas as "inferred"

### Keep Proposed vs. Accepted Clear
- Don't accept without verification
- "Proposed" is okay for uncertain areas
- Update status as you gain confidence

---

## Example: Documenting an Auth Module

### 1. Scan
```
cm_analyze(operation="scan", path="src/auth")

Output:
- 12 Python files
- Main patterns: JWT, OAuth, decorators
- Entry points: login.py, register.py
- Models: User, Token, Session
```

### 2. Propose Features
```
F001-user-auth.md (proposed)
- Login/logout functionality
- Evidence: login.py, logout.py

F002-oauth.md (proposed)
- Third-party authentication
- Evidence: oauth.py, providers/
```

### 3. Propose Decisions
```
D001-jwt-strategy.md (proposed)
- JWT with refresh tokens
- Evidence: token.py, decorators.py

D002-oauth-providers.md (proposed)
- Support Google, GitHub
- Evidence: providers/google.py, providers/github.py
```

### 4. Review and Refine
Interview original developers or code reviewers:
- Why JWT over sessions?
- Are there rate limits?
- What's the token expiry strategy?

Update proposals with verified information.

### 5. Accept
```
cm_intent(operation="update", type="feature", id="F001", status="draft")
cm_intent(operation="update", type="decision", id="D001", status="accepted")
```

---

## Common Patterns to Identify

| Pattern | Look For |
|---------|----------|
| Authentication | `auth/`, `login`, decorators, middleware |
| API Structure | Route definitions, controllers, handlers |
| Database | ORM models, migrations, repositories |
| Error Handling | Try/catch patterns, error classes |
| Logging | Logger setup, log levels, handlers |
| Configuration | `.env`, config files, settings |
| Testing | `tests/`, fixtures, mocks |

---

## Warning Signs

Watch for these red flags during extraction:

- **No clear boundaries**: Spaghetti code, circular dependencies
- **Inconsistent patterns**: Multiple ways to do the same thing
- **Dead code**: Unused functions, commented blocks
- **Missing tests**: Areas with no test coverage
- **Hardcoded values**: Magic numbers, embedded secrets

Document these as anti-patterns or tech debt items.
