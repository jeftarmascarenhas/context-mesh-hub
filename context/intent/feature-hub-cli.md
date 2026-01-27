# Feature Intent: Hub CLI (Bootstrap, Runtime, and Diagnostics)

## What

Provide a minimal but high-quality **command-line interface (CLI)** that serves as the technical entry point for Context Mesh Hub.

The CLI is responsible for:
- bootstrapping Context Mesh Hub inside a repository
- running and managing the local MCP server
- opening and managing the local UI
- providing diagnostics and guided help

The CLI does **not** implement context logic itself. It delegates domain behavior to the MCP server.

## Why

**Business Value**
- Enables fast adoption with a familiar developer workflow
- Reduces setup friction for individuals and teams
- Improves reliability and trust through clear diagnostics and guidance
- Provides a stable, enterprise-friendly entrypoint (predictable setup and supportability)

**Technical Value**
- Establishes a thin orchestration layer separating DX from domain logic
- Ensures consistent local runtime for MCP + UI across environments
- Enables reproducible initialization for greenfield and brownfield projects
- Centralizes environment checks and troubleshooting (`doctor`)

## Scope

### Bootstrap (Initialization)
- Initialize Context Mesh Hub in:
  - new repositories (greenfield)
  - existing repositories (brownfield)
- Create required structure and baseline artifacts only (no AI generation), including:
  - `context/intent/`
  - `context/decisions/`
  - `context/evolution/`
  - `context/.context-mesh-framework.md`
  - `AGENTS.md`
- Support safe initialization behavior in non-empty directories

### Runtime Management
- Start / stop / restart the local MCP server
- Report status and health checks for MCP server
- Manage configuration for local ports and paths (safe defaults)

### UI Management
- Launch the local UI (Next.js) for the current repository
- Provide clear output of the UI URL and status
- Optionally open the browser

### Diagnostics & Help
- `doctor` command that validates:
  - required runtimes and versions (Node/Python)
  - repository structure
  - port availability
  - permissions and path safety
- High-quality help output, examples, and guided remediation steps

### Out of Scope (v1)
- Creating feature intents or decisions using AI inside the CLI
- Executing arbitrary shell commands on behalf of the user
- IDE-specific integration logic
- Remote telemetry or analytics (unless explicitly opted in later)

## Acceptance Criteria

### Functional
- [ ] `cm init` can initialize Context Mesh Hub in:
  - [ ] an empty directory (greenfield)
  - [ ] a non-empty existing repository (brownfield) safely
- [ ] `cm start` starts the local MCP server for the current repository
- [ ] `cm status` reports whether MCP is running and reachable
- [ ] `cm stop` stops the local MCP server cleanly
- [ ] `cm ui` starts (or connects to) the local UI for the repository
- [ ] `cm doctor` reports actionable diagnostics and remediation steps

### Non-Functional
- [ ] CLI remains thin: no domain logic duplicated from MCP
- [ ] Output is predictable, readable, and consistent across platforms
- [ ] Clear error messages that guide the user to resolution
- [ ] Safe defaults (no destructive operations, no silent overwrites)
- [ ] Works on macOS/Linux with best-effort Windows support

## Implementation Approach

1. **Command Surface Design**
   - Define a small command set focused on adoption and runtime:
     - init
     - start/stop/restart
     - status
     - ui
     - doctor
     - help
   - Provide examples for greenfield vs brownfield usage

2. **Bootstrap Templates**
   - Ship minimal file templates for:
     - `AGENTS.md`
     - `context/.context-mesh-framework.md`
     - baseline intent/decision/evolution files (optional stubs)
   - Ensure initialization is idempotent and safe

3. **MCP Runtime Orchestration**
   - Spawn the MCP server with:
     - repository root detected
     - safe path allowlist
     - configured ports
   - Provide health checks (ping tool)

4. **UI Orchestration**
   - Start the Next.js UI with:
     - repository context passed via env/config
   - Provide URL output and readiness checks

5. **Diagnostics**
   - Implement `doctor` checks:
     - Node/Python versions
     - required binaries present
     - repository structure validation (delegating to MCP where possible)
     - port checks and conflict detection

## Constraints

- **Agnosticism**: must not depend on any specific AI agent or IDE
- **Thin layer**: CLI delegates domain behavior to MCP tools
- **Safety**: no destructive operations by default; explicit confirmations if needed
- **Repo-first**: all initialization targets repository structure and artifacts
- **Offline-friendly**: should function without internet access

## Related

- [Project Intent](./project-intent.md)
- [Feature: Hub Core](./feature-hub-core.md)
- [Feature: Hub Build Protocol](./feature-hub-build-protocol.md)
- [Feature: Hub UI](./feature-hub-ui.md)
- [Decision: Tech Stack](../decisions/001-tech-stack.md)
- [Decision: Agent Scope and Authority](../decisions/007-agent-scope-and-authority.md)

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Status**: Active
