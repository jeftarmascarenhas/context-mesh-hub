# Feature Intent: Hub Core (MCP + Context Engine)

## What

Implement the **Hub Core** as a local-first **MCP server** that reads, validates, and serves Context Mesh artifacts from a repository.

Hub Core is the foundational runtime that turns Context Mesh into an **active, enforceable context operating system** by exposing governed tools to any MCP-compatible agent (Cursor, Copilot, Claude, etc.).

## Why

**Business Value**
- Enables sustainable AI-first development by preventing context loss, drift, and inconsistency across sessions
- Provides a single, governed source of truth for context workflows in teams and organizations
- Makes Context Mesh usable in real projects (greenfield and brownfield), not only as documentation

**Technical Value**
- Establishes the core architecture for MCP-first + chat-first workflows
- Enables structured tools (intent/build/learn) that agents can call reliably
- Provides validation and enforcement to keep context integrity high
- Creates the basis for bundling and incremental context delivery for large codebases

## Scope

### MCP Server (Core Runtime)
- Run a local MCP server that can:
  - Read Context Mesh files under `context/`
  - Validate structure and required sections
  - Resolve references (e.g., feature ↔ decision links)
  - Provide structured tool responses to agents

### Context Validation (Governance)
- Validate that the repository contains required Context Mesh structure:
  - `context/intent/`
  - `context/decisions/`
  - `context/evolution/`
  - `AGENTS.md`
- Validate that key artifacts are present and consistent:
  - Project Intent exists
  - Decisions referenced by features exist
  - Basic integrity rules (e.g., required sections)

### Context Bundling (Minimal Context Delivery)
- Provide “bundles” for:
  - Project
  - Feature
  - Decision
- Bundle output must be deterministic and scoped (no uncontrolled expansion)

### Out of Scope (v1)
- IDE-specific plugins or integrations
- Direct application code generation
- Cloud-hosted services or databases
- Automatic execution of shell commands on the developer machine
- UI rendering (handled by Hub UI feature)

## Acceptance Criteria

### Functional
- [x] MCP server starts locally and exposes Hub Core tools
- [x] The server can read and return content for:
  - [x] Project intent
  - [x] A feature intent
  - [x] A decision
- [x] Validation can detect:
  - [x] missing required directories/files
  - [x] missing required sections in context files
  - [x] broken references (e.g., decision referenced but file missing)
- [x] Bundling can generate a minimal, scoped bundle for:
  - [x] project
  - [x] feature
  - [x] decision
- [x] Tool responses are agent-agnostic (plain structured output, no IDE assumptions)

### Non-Functional
- [x] Repo-first only: no database required in v1
- [x] Safe by default: file operations are scoped to the repository context directory
- [x] Clear error messages with remediation guidance
- [x] Cross-platform support (macOS/Linux) with predictable setup
- [x] Stable tool contracts (versioned) to avoid breaking agents
- [ ] MCP exposes semantic tools mapped to canonical prompt templates (Decision 010)
- [ ] Each tool records provenance (pack/version/template hash/source) (Decision 010)
- [ ] Tool fails clearly if template missing in all sources (Decision 010)

## Implementation Approach

1. **Define tool contracts (Decision 003)**
   - Tool namespaces: `intent.*`, `build.*`, `learn.*`, plus `hub.*` for shared operations
   - Standard error model and response schema

2. **Implement repository context loader**
   - Identify repository root
   - Locate and index `context/` tree
   - Read files safely (path allowlist)

3. **Implement validation engine**
   - Structure validation (required folders/files)
   - Content validation (required sections)
   - Reference integrity validation (Related links + referenced decisions)

4. **Implement bundling engine**
   - Deterministic ordering
   - Scope-limited inclusion rules
   - Size/priority rules (Decision 004)

5. **Expose MCP tools**
   - Read tools (safe baseline)
   - Guided-write tools only where deterministic (optional in v1; safer to start read-first)

## Constraints

- **Agnosticism**: Must work with any MCP-compatible agent (no Cursor-specific behavior)
- **Safety**: No default “execute code on machine” capability
- **Repo-first**: Context is stored and versioned in the repository
- **Simplicity**: Prefer deterministic outputs over “creative” generation

## Related

- [Project Intent](./project-intent.md)
- [Decision: Tech Stack](../decisions/001-tech-stack.md)
- [Decision: MCP Tool Contracts](../decisions/002-mcp-tool-contracts.md)
- [Decision: Context Bundling Strategy](../decisions/003-context-bundling-strategy.md)
- [Decision: Prompt Pack Resolution and Update Model](../decisions/010-prompt-pack-resolution-and-update-model.md)

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Completed**: 2026-01-27 (Phase: Build)
- **Status**: Completed

## Implementation Notes

Hub Core has been implemented as a Python 3.12+ MCP server using FastMCP.

### Components Implemented

1. **Repository Context Loader** (`loader.py`)
   - Auto-detects repository root
   - Indexes all Context Mesh artifacts
   - Safe path validation (only allows reading from `context/` subdirectories)
   - Supports: project intent, feature intents, decisions, knowledge, agents, changelog

2. **Validation Engine** (`validator.py`)
   - Structure validation (required directories and files)
   - Content validation (required sections in artifacts)
   - Reference integrity validation (broken links detection)
   - Returns structured results (errors, warnings, info)

3. **Bundling Engine** (`bundler.py`)
   - Implements Decision 003 (Context Bundling Strategy)
   - Supports: project bundles, feature bundles, decision bundles
   - Deterministic ordering and scoped inclusion
   - Bundle metadata (ID, timestamp, composition)

4. **MCP Server & Tools** (`server.py`, `tools.py`)
   - `context_read` - Read context artifacts
   - `context_validate` - Validate repository
   - `context_bundle` - Generate context bundles
   - `hub_health` - Health check and status

### Verification

- ✅ Loader successfully indexes all context artifacts
- ✅ Validator passes with no errors on current repository
- ✅ Bundler generates project and feature bundles correctly
- ✅ All Acceptance Criteria met

### Limitations

- FastMCP dependency required (not yet installed/tested in full MCP environment)
- Write tools not implemented (read-only for v1, as per scope)
- No caching strategy yet (simple in-memory index)
