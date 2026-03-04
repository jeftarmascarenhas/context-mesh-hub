# Context Mesh Artifact Specifications

> **For AI Agents**: This document defines the standard structure for all Context Mesh artifacts.
> Always follow these specifications when creating or updating context files.

---

## Directory Structure

```
context/
├── intent/                    # WHAT to build and WHY
│   ├── project-intent.md      # Required: Project vision
│   └── F00X-*.md              # Features (numbered sequentially)
├── decisions/                 # HOW to build (technical choices)
│   └── D00X-*.md              # Decisions (numbered sequentially)
├── knowledge/                 # Patterns and anti-patterns
│   ├── patterns/              # What to FOLLOW
│   │   └── *.md
│   └── anti-patterns/         # What to AVOID
│       └── *.md
├── agents/                    # Execution agents
│   └── agent-*.md
└── evolution/                 # History
    └── changelog.md           # Required: Change history
```

---

## 📋 Feature Intent (`context/intent/F00X-*.md`)

### Naming Convention

- **Format**: `F00X-description.md` where X is a sequential number
- **Examples**: `F001-user-authentication.md`, `F002-api-gateway.md`
- **Rules**:
  - Must start with `F` followed by 3-4 digits
  - Use lowercase with hyphens for description
  - Sequential numbering (don't skip numbers)

### Structure (Required Sections)

```markdown
---
id: F001
type: feature
title: User Authentication
status: draft | in-progress | completed | blocked | abandoned
priority: high | medium | low
created: 2024-01-15
updated: 2024-01-15
depends_on: []
decisions: [D001, D002]
agents: []
---

# Feature: [Title]

## What

[Clear description of what will be built]

## Why

[Business/technical value and justification]

## How

[High-level implementation approach - optional but recommended]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Constraints

[Technical or business constraints - optional]

## Related

- **Decision**: [DXX - Name](../decisions/DXX-*.md)
- **Feature**: [FYY - Name](./FYY-*.md)
```

### Required Fields

#### YAML Frontmatter
| Field | Required | Description |
|-------|----------|-------------|
| `id` | ✅ Yes | Feature ID (F001, F002...) |
| `type` | ✅ Yes | Always "feature" |
| `title` | ✅ Yes | Feature title |
| `status` | ✅ Yes | draft, in-progress, completed, blocked, abandoned |
| `created` | ✅ Yes | ISO date (YYYY-MM-DD) |
| `updated` | ✅ Yes | ISO date (YYYY-MM-DD) |
| `priority` | ⚠️ Recommended | high, medium, low |
| `depends_on` | ⚠️ Recommended | Array of feature IDs |
| `decisions` | ⚠️ Recommended | Array of decision IDs |
| `agents` | ❌ Optional | Array of agent IDs |

#### Markdown Content
| Field | Required | Description |
|-------|----------|-------------|
| `What` | ✅ Yes | What will be built |
| `Why` | ✅ Yes | Business/technical justification |
| `Acceptance Criteria` | ✅ Yes | Measurable success criteria (checkboxes) |
| `How` | ⚠️ Recommended | Implementation approach |
| `Constraints` | ❌ Optional | Known limitations |
| `Related` | ⚠️ Recommended | Links to decisions/features |

---

## 🎯 Decision (`context/decisions/D00X-*.md`)

### Naming Convention

- **Format**: `D00X-description.md` where X is a sequential number
- **Examples**: `D001-tech-stack.md`, `D002-auth-approach.md`
- **Rules**:
  - Must start with `D` followed by 3-4 digits
  - Use lowercase with hyphens for description
  - Sequential numbering (don't skip numbers)

### Structure (Required Sections)

```markdown
---
id: D001
type: decision
title: Tech Stack Selection
status: proposed | accepted | superseded | deprecated
created: 2024-01-10
updated: 2024-01-10
features: [F001, F002]
supersedes: null
superseded_by: null
related: []
---

# Decision: [Title]

## Context

[What situation led to this decision? What problem are we solving?]

## Decision

[The actual decision made - be explicit and specific]

## Rationale

[Why this decision? What makes it the right choice?]

## Alternatives Considered

[What other options were evaluated and why were they rejected?]

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Trade-offs
- Trade-off 1
- Trade-off 2

## Outcomes

[Added after implementation - what actually happened]

## Related

- [Feature: FXX - Name](../intent/FXX-*.md)
- [Decision: DYY - Name](./DYY-*.md)
```

### Required Fields

#### YAML Frontmatter
| Field | Required | Description |
|-------|----------|-------------|
| `id` | ✅ Yes | Decision ID (D001, D002...) |
| `type` | ✅ Yes | Always "decision" |
| `title` | ✅ Yes | Decision title |
| `status` | ✅ Yes | proposed, accepted, superseded, deprecated |
| `created` | ✅ Yes | ISO date (YYYY-MM-DD) |
| `updated` | ✅ Yes | ISO date (YYYY-MM-DD) |
| `features` | ⚠️ Recommended | Array of feature IDs |
| `supersedes` | ⚠️ Recommended | Decision ID or null |
| `superseded_by` | ⚠️ Recommended | Decision ID or null |
| `related` | ❌ Optional | Array of related artifact IDs |

#### Markdown Content
| Field | Required | Description |
|-------|----------|-------------|
| `Context` | ✅ Yes | Problem statement and background |
| `Decision` | ✅ Yes | The actual decision made |
| `Rationale` | ✅ Yes | Why this decision |
| `Alternatives Considered` | ⚠️ Recommended | Other options evaluated |
| `Consequences` | ⚠️ Recommended | Expected positive/negative effects |
| `Outcomes` | ❌ Optional | Actual results (added later) |
| `Related` | ⚠️ Recommended | Links to features/decisions |

---

## 📚 Pattern (`context/knowledge/patterns/*.md`)

### Naming Convention

- **Format**: `descriptive-name.md`
- **Examples**: `phased-refactoring-with-di.md`, `event-sourcing-pattern.md`
- **Rules**:
  - Use lowercase with hyphens
  - Descriptive, not numbered
  - Should be reusable across projects

### Structure (Required Sections)

```markdown
# Pattern: [Title]

## Context

[When should this pattern be used? What problem does it solve?]

## The Pattern

[Detailed explanation of the pattern]

## Evidence

[Real-world examples, metrics, or proof that this works]

## Why It Works

[Explanation of why this pattern is effective]

## When to Use

[Specific conditions where this pattern applies]

## When NOT to Use

[Situations where this pattern should be avoided]

## Implementation Guide

[Step-by-step instructions or code examples]

## Anti-Patterns to Avoid

[Related anti-patterns that contradict this pattern]

## Related

- **Feature**: [FXX - Name](../../intent/FXX-*.md)
- **Decision**: [DXX - Name](../../decisions/DXX-*.md)
- **Pattern**: [Other Pattern](./other-pattern.md)

## Status

- **Created**: YYYY-MM-DD
- **From**: Learn Sync | Manual Documentation
- **Confidence**: Low | Medium | High
- **Impact**: Low | Medium | High
- **Evidence**: [Links to where this was successfully applied]
```

### Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `Context` | ✅ Yes | When to use this pattern |
| `The Pattern` | ✅ Yes | Detailed explanation |
| `Evidence` | ✅ Yes | Proof it works |
| `Status` | ✅ Yes | Created date + confidence/impact |
| `When to Use` | ⚠️ Recommended | Applicability conditions |
| `When NOT to Use` | ⚠️ Recommended | Anti-conditions |
| `Implementation Guide` | ⚠️ Recommended | How to apply |
| `Related` | ⚠️ Recommended | Links to features/decisions |

---

## ❌ Anti-Pattern (`context/knowledge/anti-patterns/*.md`)

### Naming Convention

- **Format**: `descriptive-problem-name.md`
- **Examples**: `python-relative-imports-pitfall.md`, `god-object-antipattern.md`
- **Rules**:
  - Use lowercase with hyphens
  - Descriptive, not numbered
  - Should clearly identify the problem

### Structure (Required Sections)

```markdown
# Anti-Pattern: [Title]

## Context

[When does this anti-pattern occur? What situation leads to it?]

## The Problem

[Detailed explanation of the anti-pattern and why it's bad]

## Evidence

[Real-world examples where this caused issues]

## Why It Happens

[Common reasons developers fall into this trap]

## Recommendation

[How to avoid this anti-pattern]

### Pattern for nested structures:
[Correct approach with examples]

## Related

- **Feature**: [FXX - Name](../../intent/FXX-*.md)
- **Pattern**: [Correct Pattern](../patterns/correct-approach.md)

## Status

- **Created**: YYYY-MM-DD
- **From**: Learn Sync | Manual Documentation
- **Confidence**: Low | Medium | High
- **Impact**: Low | Medium | High
```

### Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `Context` | ✅ Yes | When this anti-pattern occurs |
| `The Problem` | ✅ Yes | What's wrong and why |
| `Evidence` | ✅ Yes | Real examples |
| `Recommendation` | ✅ Yes | How to avoid it |
| `Status` | ✅ Yes | Created date + confidence/impact |
| `Why It Happens` | ⚠️ Recommended | Common causes |
| `Related` | ⚠️ Recommended | Links to correct patterns |

---

## 📖 Project Intent (`context/intent/project-intent.md`)

### Structure (Required Sections)

```markdown
# Project Intent: [Project Name]

## What

[What is this project? What does it do?]

## Why

[Why does this project exist? What problem does it solve?]

### Business Value
[Business justification]

### Technical Value
[Technical justification]

## Scope

### Core Capabilities
- Capability 1
- Capability 2

### Out of Scope (v1)
- Out of scope 1
- Out of scope 2

## Acceptance Criteria

### Functional
- [ ] Criterion 1
- [ ] Criterion 2

### Non-Functional
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints

[Technical, business, or organizational constraints]

## Related

- [Feature: F001 - Name](./F001-*.md)
- [Decision: D001 - Name](../decisions/D001-*.md)

## Status

- **Created**: YYYY-MM-DD
- **Status**: Active
```

### Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `What` | ✅ Yes | Project description |
| `Why` | ✅ Yes | Business/technical value |
| `Scope` | ✅ Yes | What's in and out of scope |
| `Acceptance Criteria` | ✅ Yes | Success criteria |
| `Status` | ✅ Yes | Created date + status |
| `Constraints` | ⚠️ Recommended | Known limitations |
| `Related` | ⚠️ Recommended | Links to features/decisions |

---

## 📝 Changelog (`context/evolution/changelog.md`)

### Structure (Required Sections)

```markdown
# Changelog

[Introduction paragraph explaining this file]

---

## YYYY-MM-DD - [Event Name]

**What Changed:**
- Change 1
- Change 2

**Why:**
[Justification for the change]

**Outcomes:**
- Outcome 1
- Outcome 2

**Related:**
- Feature: [FXX - Name](../intent/FXX-*.md)
- Decision: [DXX - Name](../decisions/DXX-*.md)

**Next Steps:**
- Next step 1
- Next step 2

---

[More entries in reverse chronological order]
```

### Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| Date header | ✅ Yes | `YYYY-MM-DD - Event Name` |
| `What Changed` | ✅ Yes | What changed |
| `Why` | ✅ Yes | Why it changed |
| `Related` | ⚠️ Recommended | Links to artifacts |
| `Outcomes` | ❌ Optional | Results of the change |
| `Next Steps` | ❌ Optional | Future actions |

---

## 🤖 Agent File (`context/agents/agent-*.md`)

### Naming Convention

- **Format**: `agent-descriptive-name.md`
- **Examples**: `agent-feature-executor.md`, `agent-learn-sync.md`

### Structure (Required Sections)

```markdown
# Agent: [Name]

## Purpose

[What does this agent do?]

## Context Files to Load

- `@context/intent/project-intent.md`
- `@context/decisions/D*.md`
- [Other required files]

## Steps

1. Step 1 description
2. Step 2 description
3. Step 3 description

## Definition of Done

- [ ] DoD criterion 1
- [ ] DoD criterion 2
- [ ] DoD criterion 3

## Constraints

[Execution constraints or boundaries]

## Related

- [Feature: FXX - Name](../intent/FXX-*.md)
- [Decision: DXX - Name](../decisions/DXX-*.md)
```

### Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `Purpose` | ✅ Yes | What this agent does |
| `Context Files to Load` | ✅ Yes | Required context |
| `Steps` | ✅ Yes | Execution steps |
| `Definition of Done` | ✅ Yes | Success criteria |
| `Constraints` | ⚠️ Recommended | Boundaries |
| `Related` | ⚠️ Recommended | Links to artifacts |

---

## 🎯 Validation Rules

### General Rules

1. **All artifact files MUST use UTF-8 encoding**
2. **All artifact files MUST use Unix line endings (LF)**
3. **All required sections MUST be present** (empty is allowed if not applicable)
4. **All dates MUST use ISO 8601 format** (`YYYY-MM-DD`)
5. **All links MUST use relative paths** from the current file
6. **Feature/Decision numbering MUST be sequential** (F001, F002, F003...)

### Cross-Reference Rules

1. **All Related sections MUST use valid relative paths**
2. **All referenced artifacts MUST exist**
3. **Circular references are allowed** (bidirectional links)
4. **Dead links are NOT allowed** (will fail validation)

---

## 📚 Progressive Disclosure

Context Mesh artifacts follow progressive disclosure:

1. **Metadata** (~50 tokens): File name + status
2. **Summary** (~200 tokens): What + Why + Status
3. **Full Content** (~1000-5000 tokens): Complete artifact loaded on demand
4. **Related Artifacts** (as needed): Loaded when referenced

**Best Practices:**
- Keep individual artifacts under 500 lines
- Move detailed technical content to separate files
- Use Related sections to link to deep-dive documentation
- Avoid deeply nested reference chains (max 2 levels)

---

## 🔍 Tools to Query Specifications

AI Agents can use these MCP tools to get specifications:

- `cm_intent(action="spec")` - Get feature/decision spec
- `cm_validate()` - Validate artifact structure
- `cm_status()` - Get current project structure

**Example:**
```python
# Get specification for creating a new feature
spec = cm_intent(action="spec", type="feature")
print(spec["required_sections"])  # ['What', 'Why', 'Acceptance Criteria', 'Status']
print(spec["optional_sections"])  # ['How', 'Constraints', 'Related']
print(spec["example"])             # Full example feature
```

---

## Status

- **Created**: 2026-03-04
- **Version**: 1.0.0
- **Applies to**: Context Mesh Hub v0.2.0+
