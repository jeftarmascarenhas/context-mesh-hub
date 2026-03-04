---
id: D014
type: decision
title: Brownfield Extraction - Artifact Classification Strategy
status: accepted
created: 2026-03-04
updated: 2026-03-04
features: [F001]
supersedes: null
superseded_by: null
related: [D005]
---

# Decision: Brownfield Extraction - Artifact Classification Strategy

## Context

The cm_analyze tool was incorrectly suggesting 'Feature Intent' artifacts for technical components like server.py, main.py, and entry point files. This violated Context Mesh 1.1.0 principles where:

- **Features** represent user/system-facing capabilities that deliver value
- **Decisions** document technical choices and architecture
- **Patterns** capture reusable code approaches
- **Knowledge** stores domain expertise and constraints

The incorrect classification created noise and confusion, mixing "WHAT provides value" with "HOW it's implemented".

## Decision

Brownfield extraction (cm_analyze) must classify artifacts correctly according to Context Mesh 1.1.0:

### Feature Intent (`feature-*.md`)
**Only for capabilities that deliver direct value to users or the system as a product.**

Examples that SHOULD be features:
- "User Authentication" - users can log in
- "Todo CRUD Operations" - users can manage todos
- "Build Protocol" - system provides governed builds
- "Brownfield Analysis" - system can analyze existing code

Examples that should NOT be features:
- "server.py" - this is implementation, not a feature
- "main.py" - this is an entry point, not a feature
- "database connection" - this is infrastructure
- Individual files or modules

### Technical Decision (`decisions/*.md`)
**For technical and architectural choices with clear evidence.**

Extraction should propose decisions for:
- **Tech Stack**: pyproject.toml, package.json
- **Dependency Management**: uv.lock, requirements.txt, yarn.lock
- **Framework Choice**: Presence of FastAPI, React, Django files
- **Database Choice**: Prisma schema, migrations folder
- **Build Tools**: Makefile, docker-compose.yml
- **Testing Strategy**: Test file patterns and frameworks

### Patterns/Anti-Patterns (`knowledge/patterns/`, `knowledge/anti-patterns/`)
**For reusable code approaches or practices to avoid.**

Examples:
- API design patterns from consistent endpoint structures
- Error handling patterns from try/catch usage
- Authentication patterns from decorator usage
- Anti-pattern: Direct database access instead of ORM

### Knowledge (`knowledge/`)
**For domain knowledge, constraints, or architectural insights.**

Examples:
- Domain terminology and business rules
- System constraints and limitations
- Integration requirements

## Rationale

1. **Aligns with Context Mesh 1.1.0**: Features document value delivery, Decisions document technical choices
2. **Reduces Noise**: Stops proposing dozens of meaningless "Feature: main" artifacts
3. **Focuses on Value**: Extraction identifies what the system DOES (features) vs HOW it does it (decisions)
4. **Evidence-Based**: Decisions must reference concrete files (pyproject.toml, Dockerfile, etc.)
5. **Principle Compliance**: "Context is primary, code is manifestation" - we document intent and decisions, not individual files

## Alternatives Considered

### Keep Current Approach
- **Pros**: No refactoring needed
- **Cons**: Violates Context Mesh principles, creates confusion, generates useless proposals
- **Rejected**: Fundamentally incorrect interpretation of the framework

### Tag Everything as "Suspected"
- **Pros**: Let humans sort it out
- **Cons**: Abdicates responsibility of intelligent extraction
- **Rejected**: Tool should provide intelligent classification, not dump everything

## Consequences

### Positive
- Cleaner brownfield extraction with fewer, higher-quality proposals
- Correct artifact classification aligned with Context Mesh 1.1.0
- Proposals focus on system capabilities (features) and technical choices (decisions)
- Less noise for humans to review

### Negative
- Requires refactoring brownfield.py extraction logic
- May produce fewer proposals initially (but higher quality)
- Need to update tests and documentation

## Related

- [Decision: Brownfield Context Extraction](./D005-brownfield-context-extraction.md)
- [Decision: MCP Simplification](./D013-mcp-simplification.md)
- [Feature: Hub Brownfield](../intent/F001-hub-brownfield.md)

## Status

- **Created**: 2026-03-03
- **Status**: Accepted
