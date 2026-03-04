# Decision: Technology Stack

## Context

Context Mesh Hub must operate as a **local-first**, **repository-first**, and **agent-agnostic** system.

The technology stack must:
- Support MCP-based integrations
- Enable structured context validation and bundling
- Be safe by default (no uncontrolled execution)
- Work across different operating systems
- Be suitable for open source distribution
- Support both CLI-based and UI-based interactions

The stack must also align with the long-term goal of positioning Context Mesh as a standard for AI-first development.

## Decision

Adopt a **multi-layered architecture** with clear separation of responsibilities:

### MCP Server (Core Runtime)
- **Language**: Python 3.12+
- **Protocol**: Model Context Protocol (MCP)
- **Framework**: FastMCP (stable 2.x line)

**Responsibilities**
- Context validation and enforcement
- Context bundling and scoping
- Greenfield and brownfield analysis pipelines
- Build governance (Plan / Approve / Execute)
- Learn synchronization

---

### CLI (Bootstrap & Runtime Control)
- **Runtime**: Python 3.12+
- **Framework**: Typer + Rich
- **Package Manager**: uv (or pip)

**Responsibilities**
- Initialize Context Mesh Hub with AI agent selection (`cm init --ai`)
- Generate MCP configuration for editors (`cm config`)
- Provide environment diagnostics (`cm doctor`)
- Start the local UI (`cm ui`)
- Support AI agent backends: Cursor, Copilot, Gemini CLI, Claude Code
- Act as a thin orchestration layer only

---

### Local UI (Developer Experience)
- **Framework**: Next.js v16 (latest)
- **Execution Model**: Local build and runtime

**Responsibilities**
- Display project and context status
- Allow navigation of Intent / Build / Learn artifacts
- Guide developers through Context Mesh workflows
- Surface warnings, errors, and recommendations from the MCP

---

### Storage Model
- **Primary Storage**: File system (Git repository)
- **Database**: None (v1)

All context artifacts live under the `context/` directory and are versioned using Git.

## Rationale

- **Python for MCP + CLI** provides stack unification and strong alignment with AI tooling ecosystems
- **FastMCP** is the standard for MCP server implementation in Python
- **Typer + Rich** provides excellent DX for CLI with beautiful terminal output
- **Next.js** enables a modern, maintainable UI without coupling business logic to the frontend
- **Repository-first storage** ensures transparency, auditability, and easy adoption
- Clear separation of concerns reduces complexity and improves long-term maintainability

## Alternatives Considered

### Node.js CLI + Python MCP (Original v1)
- **Pros**: Familiar CLI tooling, TypeScript type safety
- **Cons**: Two languages to maintain, complex dependency management
- **Decision**: Rejected in favor of Python unification (2026-01-28)

### Single-stack Node.js implementation
- **Pros**: Fewer languages, simpler tooling
- **Cons**: Weaker MCP ecosystem maturity
- **Decision**: Rejected in favor of stronger MCP-native support

### Database-backed context storage
- **Pros**: Query flexibility, centralization
- **Cons**: Operational complexity, reduced transparency
- **Decision**: Rejected for v1

### IDE-specific extensions
- **Pros**: Tighter UX integration
- **Cons**: Vendor lock-in, reduced portability
- **Decision**: Rejected to preserve agent and IDE agnosticism

## Consequences

### Positive
- Strong alignment with Context Mesh principles
- High portability and adoption potential
- Safe, inspectable, and auditable system
- Clear layering between runtime, orchestration, and UX
- **Stack unification**: Python for MCP and CLI simplifies maintenance

### Trade-offs
- Requires Python 3.12+ (may need installation on some systems)
- Requires discipline in context management
- UI depends on MCP cooperation rather than direct file access

## Outcomes

### Implementation: F006 Hub-Core Refactoring (2026-03-04)

**What Was Implemented:**
- Complete 3-layer architecture (Domain/Infrastructure/MCP) as specified in this decision
- 28 new files replacing 4 monolithic files (3,673 lines removed, ~6,000 lines of structured code added)
- Dependency Injection throughout domain services
- File-based persistence in `.context-mesh/` (no database needed for v1 ✅)
- Zero breaking changes to MCP interface

**Learnings:**
- ✅ **3-layer architecture validated** - Clear separation of concerns dramatically improved maintainability
- ✅ **DI pattern successful** - Constructor-based DI made services testable with mocks
- ✅ **File-based persistence sufficient** - JSON storage in `.context-mesh/` works well for plans/proposals
- ✅ **Phased approach critical** - 5 phases allowed incremental validation without breaking production
- ⚠️ **Python relative imports tricky** - Deep nesting (`mcp/tools/*.py`) caused import path confusion (see [Anti-Pattern](../knowledge/anti-patterns/python-relative-imports-pitfall.md))
- ⚠️ **Context Mesh workflow must be followed** - Initially violated workflow by creating REFACTORING_PLAN.md outside Context Mesh structure; corrected by creating proper feature intent F006

**Evidence:**
- Feature: [F006 - Refactor Hub-Core Architecture](../intent/F006-refactor-hub-core-architecture.md)
- Pattern: [Phased Refactoring with DI](../knowledge/patterns/phased-refactoring-with-di.md)
- Learn Sync: proposal ed8afea3-4901-4041-a79a-108d2e764259

**Recommendation:**
Continue this architectural approach for other components (CLI, UI). The 3-layer pattern with DI and file-based persistence proved highly effective.

---

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: F006 - Refactor Hub-Core Architecture](../intent/F006-refactor-hub-core-architecture.md)

## Status

- **Created**: 2026-01-26
- **Updated**: 2026-03-04 (added outcomes from F006)
- **Status**: Accepted
