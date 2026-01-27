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
- **Runtime**: Node.js (Active LTS)
- **Language**: TypeScript
- **Package Manager**: pnpm

**Responsibilities**
- Initialize Context Mesh Hub in a repository
- Start and stop the MCP server
- Provide environment diagnostics (`doctor`)
- Open the local UI
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

- **Python + MCP** provides strong alignment with AI tooling ecosystems and structured analysis workflows
- **Node.js + TypeScript** offers excellent DX for CLI tooling and cross-platform support
- **Next.js** enables a modern, maintainable UI without coupling business logic to the frontend
- **Repository-first storage** ensures transparency, auditability, and easy adoption
- Clear separation of concerns reduces complexity and improves long-term maintainability

## Alternatives Considered

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

### Trade-offs
- Multi-language maintenance
- Requires discipline in context management
- UI depends on MCP cooperation rather than direct file access

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: Hub UI](../intent/feature-hub-ui.md)

## Status

- **Created**: 2026-01-26
- **Status**: Accepted
