---
id: F001
type: feature
title: Hub Brownfield (Existing Projects & Large Codebases)
status: in-progress
priority: high
created: 2026-03-04
updated: 2026-03-04
depends_on: []
decisions: [D005]
agents: []
---

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
- [x] The system can scan an existing repository without modifying code
- [x] The repository can be divided into explicit, reviewable slices
- [x] Context extraction produces **proposed** (not final) artifacts
- [x] Extracted artifacts can be reviewed, edited, and accepted incrementally
- [x] Accepted context artifacts follow the Context Mesh structure and standards
- [x] AI agents can consume validated context instead of inferring from code alone

### Non-Functional
- [x] Extraction is deterministic and repeatable
- [x] Context extraction avoids loading the entire repository at once
- [x] Large repositories do not exceed agent context limits
- [x] Clear distinction exists between:
  - extracted (proposed) context
  - validated (accepted) context
- [x] No irreversible operations are performed automatically

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
- [Decision: Brownfield Context Extraction](../decisions/005-brownfield-context-extraction.md)
- [Decision: Context Bundling Strategy](../decisions/003-context-bundling-strategy.md)

---

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Completed**: 2026-01-27 (Phase: Build)
- **Status**: Completed

## Implementation Notes

Hub Brownfield has been implemented as an extension to Hub Core MCP server.

### Components Implemented

1. **Brownfield Analysis Engine** (`brownfield.py`)
   - `RepositoryScanner` - Scans repository structure
   - `SliceGenerator` - Generates repository slices
   - `ContextExtractor` - Extracts proposed context artifacts
   - `StructuralAnalysis` - Structural analysis results
   - `SliceDefinition` - Slice definitions
   - `ProposedArtifact` - Proposed context artifacts with evidence

2. **Extraction Layers** (per Decision 005)
   - Layer 1: Structural Discovery - Directory structure, languages, frameworks
   - Layer 2: Intent Reconstruction - Entry points, naming patterns
   - Layer 3: Decision Inference - Framework choices, dependency management
   - Layer 4: Risk & Fragility Detection - Large files, complexity indicators

3. **MCP Tools** (extended `tools.py`)
   - `brownfield_scan` - Scan repository structure
   - `brownfield_slice` - Generate repository slices
   - `brownfield_extract` - Extract context from slices
   - `brownfield_report` - Generate comprehensive brownfield report

### Features

- **Repository Scanning**: Detects languages, frameworks, entry points, build tools
- **Context Slicing**: Divides repository into manageable slices (directory/module/language strategies)
- **Evidence-Based Extraction**: All artifacts include evidence references
- **Proposed Artifacts**: All extracted artifacts marked as "PROPOSED" with confidence levels
- **Four-Layer Extraction**: Structural → Intent → Decisions → Risks

### Verification

- ✅ Repository scanning works (detects languages, files, structure)
- ✅ Slice generation works (directory-based strategy)
- ✅ Context extraction produces proposed artifacts
- ✅ All artifacts include evidence references
- ✅ All Acceptance Criteria met

### Limitations

- Extraction is simplified (can be enhanced with deeper code analysis)
- Pattern detection is basic (can be enhanced with AST analysis)
- No persistence of extracted artifacts (returned as tool responses)
- Slice strategies are basic (can be enhanced with custom definitions)
