# Feature Intent: Hub Brownfield (Existing Projects & Large Codebases)

## What

Enable Context Mesh Hub to operate effectively on **existing (brownfield) projects**, including large and complex codebases, by extracting, structuring, and governing context in an **incremental, evidence-based, and human-validated** manner.

This feature allows teams to adopt Context Mesh without rewriting history, freezing development, or requiring full upfront documentation.

## Why

**Business Value**
- Makes Context Mesh viable for real-world systems, not only new projects
- Reduces risk in maintaining and evolving legacy or long-lived codebases
- Creates clarity around intent and decisions that were previously implicit
- Enables safer AI-assisted changes in complex systems

**Technical Value**
- Provides a controlled mechanism for extracting context from large repositories
- Prevents AI agents from hallucinating architecture or intent
- Enables incremental context formalization without blocking development
- Establishes a repeatable approach for reasoning about complex systems

## Scope

### Brownfield Analysis
- Analyze existing repositories to understand:
  - Directory structure
  - Language and framework usage
  - Module and boundary candidates
  - High-change or high-risk areas
- Operate without modifying application code

### Context Slicing
- Divide the repository into **manageable slices** based on:
  - Directory boundaries
  - Logical modules
  - Architectural layers
  - Explicit developer input
- Each slice must be independently analyzable and reviewable

### Context Extraction
- Extract **proposed** context artifacts from each slice:
  - Feature intents (What / Why)
  - Technical and architectural decisions
  - Recurrent patterns and anti-patterns
- All extracted context must be explicitly marked as *proposed*, not accepted

### Human Validation
- Require explicit human review before:
  - Accepting extracted intents
  - Accepting extracted decisions
  - Promoting patterns to knowledge artifacts
- Support partial acceptance and iterative refinement

### Incremental Adoption
- Allow teams to:
  - Start with a single slice
  - Gradually expand coverage
  - Mix documented and undocumented areas safely

---

## Acceptance Criteria

### Functional
- [ ] The system can scan an existing repository without modifying code
- [ ] The repository can be divided into explicit, reviewable slices
- [ ] Context extraction produces **proposed** (not final) artifacts
- [ ] Extracted artifacts can be reviewed, edited, and accepted incrementally
- [ ] Accepted context artifacts follow the Context Mesh structure and standards
- [ ] AI agents can consume validated context instead of inferring from code alone

### Non-Functional
- [ ] Extraction is deterministic and repeatable
- [ ] Context extraction avoids loading the entire repository at once
- [ ] Large repositories do not exceed agent context limits
- [ ] Clear distinction exists between:
  - extracted (proposed) context
  - validated (accepted) context
- [ ] No irreversible operations are performed automatically

## Implementation Approach

1. **Repository Scan**
   - Detect languages, frameworks, and structural patterns
   - Identify candidate slices based on directories and boundaries

2. **Slice Definition**
   - Create explicit slice definitions
   - Allow developer override or refinement
   - Store slice metadata as context artifacts (not code comments)

3. **Evidence-Based Extraction**
   - Extract context based on:
     - File structure
     - Naming conventions
     - Explicit configuration files
     - Dependency relationships
   - Avoid speculative or inferred intent without evidence

4. **Proposed Context Generation**
   - Generate draft feature intents and decisions
   - Clearly label all generated artifacts as *Proposed*
   - Include references to the evidence used

5. **Human Review Loop**
   - Require explicit approval before promotion to accepted context
   - Support iterative refinement instead of all-or-nothing acceptance

6. **Progressive Expansion**
   - Repeat extraction slice by slice
   - Build a progressively richer and more reliable context mesh

---

## Constraints

- **No hallucinated intent**: all extracted context must be traceable to evidence
- **Human-in-the-loop**: no automatic acceptance of extracted context
- **Incremental only**: no requirement to document the entire system upfront
- **Safe by default**: read-only analysis unless explicitly authorized
- **Agent-agnostic**: extraction must not rely on IDE-specific behavior

---

## Related

- [Project Intent](./project-intent.md)
- [Feature: Hub Core](./feature-hub-core.md)
- [Feature: Hub Build Protocol](./feature-hub-build-protocol.md)
- [Decision: Brownfield Extraction Pipeline](../decisions/005-brownfield-extraction-pipeline.md)
- [Decision: Context Bundling Strategy](../decisions/004-context-bundling-strategy.md)

---

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Status**: Active
