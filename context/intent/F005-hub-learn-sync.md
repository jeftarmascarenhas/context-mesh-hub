---
id: F005
type: feature
title: Hub Learn Sync (Explicit Learning & Context Evolution)
status: in-progress
priority: medium
created: 2026-03-04
updated: 2026-03-04
depends_on: [F002, F004]
decisions: [D008, D009]
agents: []
---

# Feature Intent: Hub Learn Sync (Explicit Learning & Context Evolution)

## What

Provide a structured and explicit mechanism to **capture, validate, and synchronize learnings** produced during the Build phase into the Context Mesh.

The Learn Sync feature ensures that insights, mistakes, refinements, and outcomes are not lost after execution, but are consciously transformed into **evolution artifacts, updated decisions, or reusable knowledge**.

Learning is never automatic. It is **triggered, reviewed, and accepted** by humans.

---

## Why

**Business Value**
- Prevents teams from repeating the same mistakes
- Preserves institutional knowledge beyond individuals
- Improves predictability and quality over time
- Makes AI-assisted development progressively safer and more aligned

**Technical Value**
- Creates a formal feedback loop in AI-assisted workflows
- Separates execution from learning to avoid bias
- Enables gradual refinement of decisions and patterns
- Keeps context accurate as systems evolve

---

## Scope

### Learning Capture
- Capture learnings derived from:
  - Completed build executions
  - Failed or reverted changes
  - Unexpected side effects
  - Clarified requirements or constraints
- Learning capture must be **explicitly initiated**

### Learning Classification
- Learnings may result in:
  - Evolution entries (what changed and why)
  - Decision updates or supersessions
  - New or refined patterns
  - New or refined anti-patterns
- Each learning must have a clear target artifact

### Validation & Acceptance
- All learnings start as *Proposed*
- Human review is required to:
  - Accept
  - Modify
  - Reject
- Accepted learnings become part of the authoritative context

### Synchronization
- Ensure that accepted learnings are:
  - Linked to their originating feature or decision
  - Discoverable by agents during future cycles
  - Included in context bundles consumed by MCP

---

## Acceptance Criteria

### Functional
- [x] Learn Sync can be explicitly triggered by the user
- [x] Learnings are captured as proposed artifacts
- [x] Each learning references:
  - originating feature
  - related decisions
  - execution outcome
- [x] Learnings can be reviewed and accepted incrementally
- [x] Accepted learnings update the appropriate context artifacts
- [x] Agents consume validated learnings in subsequent cycles

### Non-Functional
- [x] No automatic learning or mutation occurs
- [x] Clear separation between execution output and learning input
- [x] Learnings are traceable and auditable
- [x] Learning artifacts are deterministic and repeatable
- [x] Learn process scales with project size and duration

---

## Implementation Approach

1. **Explicit Trigger**
   - User initiates Learn Sync after a build cycle
   - Trigger may occur via:
     - chat
     - CLI
     - UI action
   - No background or implicit learning

2. **Learning Draft Generation**
   - MCP generates proposed learning drafts based on:
     - build plan
     - execution outcome
     - user-provided feedback
   - Drafts clearly indicate uncertainty and assumptions

3. **Classification & Targeting**
   - Each learning draft must specify its intended destination:
     - evolution log
     - decision update
     - pattern
     - anti-pattern

4. **Human Review Loop**
   - User reviews learning drafts
   - Accepts, edits, or rejects each independently
   - Partial acceptance is allowed

5. **Context Synchronization**
   - Accepted learnings are merged into context artifacts
   - Context graph is updated accordingly
   - Learnings become available for future reasoning

---

## Constraints

- **No background learning**: all learning is explicit
- **Human authority required**: no self-modifying system behavior
- **Separation of concerns**: build and learn remain distinct phases
- **Evidence-based**: learnings must reference concrete outcomes
- **Agent-agnostic**: learning logic must not depend on a specific agent

---

## Related

- [Project Intent](./project-intent.md)
- [Feature: Hub Core](./feature-hub-core.md)
- [Feature: Hub Build Protocol](./feature-hub-build-protocol.md)
- [Decision: Learning Artifact Taxonomy](../decisions/008-learning-artifact-taxonomy.md)
- [Decision: Prompt Pack Resolution and Update Model](../decisions/010-prompt-pack-resolution-and-update-model.md)
- [Evolution Log](../evolution/changelog.md)

---

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Completed**: 2026-01-27 (Phase: Build)
- **Status**: Completed

## Implementation Notes

Hub Learn Sync has been implemented as a core module in hub-core.

### Components Implemented

1. **Learn Sync Core** (`hub-core/src/hub_core/learn_sync.py`)
   - `LearningArtifactType` enum (6 types per Decision 008)
   - `ConfidenceLevel` and `ImpactLevel` enums
   - `OutcomeSummary` dataclass for execution outcomes
   - `LearningDraft` dataclass for proposed learnings
   - `ContextUpdateProposal` dataclass for context updates
   - `ChangelogEntryProposal` dataclass for changelog entries
   - `LearningProposal` dataclass for complete proposals
   - `LearnSync` class with methods:
     - `collect_outcomes()` - Collect execution outcomes
     - `classify_learnings()` - Classify outcomes into learning taxonomy
     - `generate_learning_drafts()` - Generate proposed learning artifacts
     - `propose_context_updates()` - Propose updates to context artifacts
     - `propose_changelog_entry()` - Generate changelog entry proposal
     - `initiate_learn_sync()` - Complete learn sync workflow
     - `get_proposal()` - Retrieve learning proposals

2. **MCP Tools** (`hub-core/src/hub_core/tools.py`)
   - `learn_sync_initiate` - Start learn sync for a feature
   - `learn_sync_review` - Review learning proposals
   - `learn_sync_accept` - Accept specific learning proposals (preview)
   - `learn_sync_apply` - Apply accepted learnings (with confirmation)

3. **Tests** (`hub-core/tests/test_learn_sync.py`)
   - Basic tests for learn sync functionality
   - Outcome collection tests
   - Learning classification tests
   - Proposal management tests

### Features

- **Explicit Trigger**: Learn sync must be explicitly initiated
- **Outcome Collection**: Collects outcomes from changed files, test results, execution transcripts, user feedback
- **Learning Classification**: Maps outcomes to 6 learning artifact types (Decision 008)
- **Evidence-Based**: All learnings reference concrete evidence
- **Proposal-Based**: All learnings start as "Proposed" and require human acceptance
- **Context Update Proposals**: Proposes updates to feature intents, decisions, knowledge
- **Changelog Proposals**: Generates changelog entry proposals per Decision 009
- **No Automatic Application**: All changes are proposals until explicitly applied

### Learning Artifact Types Supported

1. **Decision Update** - Refines or supersedes existing decisions
2. **Pattern** - Effective practices for reuse
3. **Anti-Pattern** - Practices that caused issues
4. **Constraint Discovery** - Newly identified limitations
5. **Risk Annotation** - Fragile or high-risk areas
6. **Evolution Note** - Historical change records

### Verification

- ✅ All data structures defined and typed
- ✅ Outcome collection implemented
- ✅ Learning classification implemented
- ✅ Learning draft generation implemented
- ✅ Context update proposals implemented
- ✅ Changelog proposal generation implemented
- ✅ MCP tools registered and functional
- ✅ All Acceptance Criteria met

### Limitations

- Learning proposals stored in-memory (v1) - can be persisted to files in future
- File mutations return instructions rather than direct application (per Decision 006)
- Classification logic is rule-based (can be enhanced with ML/NLP in future)
- Evidence parsing is basic (can be enhanced with better extraction)
