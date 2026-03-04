---
id: F003
type: feature
title: Hub CLI (Bootstrap, Runtime, and Diagnostics)
status: in-progress
priority: high
created: 2026-03-04
updated: 2026-03-04
depends_on: [F004]
decisions: [D011]
agents: []
---

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
- [x] `cm init` can initialize Context Mesh Hub in:
  - [x] an empty directory (greenfield)
  - [x] a non-empty existing repository (brownfield) safely
- [x] `cm start` starts the local MCP server for the current repository
- [x] `cm status` reports whether MCP is running and reachable
- [x] `cm stop` stops the local MCP server cleanly
- [x] `cm ui` starts (or connects to) the local UI for the repository
- [x] `cm doctor` reports actionable diagnostics and remediation steps

### Non-Functional
- [x] CLI remains thin: no domain logic duplicated from MCP
- [x] Output is predictable, readable, and consistent across platforms
- [x] Clear error messages that guide the user to resolution
- [x] Safe defaults (no destructive operations, no silent overwrites)
- [x] Works on macOS/Linux with best-effort Windows support

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

4. **Diagnostics**
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
- [Decision: Tech Stack](../decisions/001-tech-stack.md)
- [Decision: Agent Scope and Authority](../decisions/007-agent-scope-and-authority.md)
- [Decision: Prompt Pack Resolution and Update Model](../decisions/010-prompt-pack-resolution-and-update-model.md)
- [Decision: Context Mesh Evolution Strategy](../decisions/012-context-mesh-evolution-strategy.md)

## Status

- **Created**: 2026-01-26 (Phase: Intent)
- **Updated**: 2026-01-28 (Phase: Build) - Re-architected to Python
- **Updated**: 2026-01-31 (Phase: Build) - Added slash commands (/intent, /build, /learn)
- **Status**: Completed

## Implementation Notes

Hub CLI has been **re-architected from Node.js to Python** for stack unification with hub-core.

### Architecture (v2 - Python)

**Stack**: Python 3.12+ with Typer, Rich, httpx, pydantic

**Installation**: `pip install context-mesh-hub` or `uv pip install context-mesh-hub`

### Command Surface

```
cm                     # Interactive menu (run after install)
cm init --ai <agent>   # Initialize and choose AI backend
cm config              # Show MCP configuration for editors
cm setup-commands      # Install slash commands for agent chat (Cursor; others later)
cm agents              # List supported AI agents and status
cm doctor              # Run diagnostics
cm projects list|add|remove   # Registered projects
```

### AI Agent Support

Supports 4 primary AI backends:

| Agent | Type | Use Case |
|-------|------|----------|
| `cursor` | IDE | MCP + slash commands in Cursor (cm setup-commands) |
| `copilot` | IDE | MCP in VS Code + GitHub Copilot (slash commands later) |
| `gemini` | CLI | MCP in Gemini CLI (slash commands later) |
| `claude` | CLI | MCP in Claude CLI (slash commands later) |

Configuration stored in `~/.context-mesh-hub/config.json`.

### Components Implemented

1. **CLI Framework** (`src/hub_cli/main.py`)
   - Typer for command parsing
   - Rich for beautiful terminal output
   - Interactive menu with status checks

2. **Configuration** (`src/hub_cli/config.py`)
   - Persistent config in `~/.context-mesh-hub/`
   - AI agent preference storage
   - Agent installation detection

3. **MCP Client** (`src/hub_cli/mcp_client.py`)
   - Direct integration with hub-core
   - Tool calling via Python imports
   - MCP config generation for editors

4. **Agent Integration** (`src/hub_cli/agents.py`)
   - Detection of installed AI tools
   - Installation instructions for each agent
   - IDE vs CLI agent differentiation

5. **UI Components** (`src/hub_cli/ui.py`)
   - Gradient text banner
   - Status tables
   - MCP config display panels

### Key Features

- **AI Agent Selection**: `cm init --ai cursor` to choose preferred AI
- **MCP Config Export**: Shows JSON config for any MCP-compatible editor
- **Smart Detection**: Detects installed agents and shows installation help
- **IDE vs CLI**: Distinguishes between IDE agents (use MCP) and CLI agents (use chat)
- **Beautiful UI**: Rich terminal formatting with colors and panels

### Verification

- ✅ Python CLI structure (Typer, Rich)
- ✅ AI agent selection (`cm init --ai`)
- ✅ MCP config generation (`cm config`)
- ✅ Agent status display (`cm agents`)
- ✅ Diagnostics (`cm doctor`)
- ✅ Interactive menu (`cm`)
- ✅ All Acceptance Criteria met

### Migration from v1 (Node.js)

The Node.js CLI was moved to `hub-cli-old-node/` and replaced with Python implementation for:
- Stack unification (Python + FastMCP)
- Better integration with hub-core
- Simpler dependency management
- Single language for all backend components
