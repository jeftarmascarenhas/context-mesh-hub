---
id: D011
type: decision
title: Distribution and Installation Strategy
status: accepted
created: 2026-03-04
updated: 2026-03-04
features: [F003]
supersedes: null
superseded_by: null
related: []
---

# Decision: Distribution and Installation Strategy

## Context

Context Mesh Hub consists of three components:
- **hub-core**: MCP server (Python)
- **hub-cli**: Command-line interface (Python)
- **hub-ui**: Web dashboard (Next.js)

Users need a simple way to install and use Context Mesh Hub in their projects.

Requirements:
- Single command installation
- Works on macOS, Linux, Windows
- No complex setup or configuration
- Supports both global and project-local installation
- Compatible with AI editors (Cursor, VS Code, Claude Desktop)

## Decision

### Installation Strategy: uv tool install

Distribute `context-mesh-hub-cli` as a Python tool installable via `uv tool install`.

**Installation commands:**

```bash
# Persistent installation (recommended)
uv tool install context-mesh-hub-cli --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli

# One-time usage
uvx --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli cm --help

# Upgrade
uv tool install context-mesh-hub-cli --force --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli

# Uninstall
uv tool uninstall context-mesh-hub-cli
```

**Reference**: `uv tool install` provides a single-command install and is widely used for Python CLI tools.

### Package Structure

```
context-mesh-hub/
├── pyproject.toml          # Single package definition
├── src/
│   ├── hub_core/           # MCP server
│   └── hub_cli/            # CLI
```

### Entry Points

```toml
[project.scripts]
cm = "hub_cli.main:app"
```

### UI Distribution

The UI (hub-ui) is distributed separately as it requires Node.js:

1. **Option A**: Bundled static build (no Node.js required)
2. **Option B**: npm package (`npx context-mesh-hub-ui`)
3. **Option C**: Docker image

For v1, use **Option B** with npm.

### Complete Installation Flow

```bash
# 1. Install CLI + MCP
pip install context-mesh-hub

# 2. Initialize in a project
cm init --ai cursor

# 3. Get MCP config
cm config

# 4. (Optional) Start UI
cm ui  # Requires Node.js
```

## Rationale

- **PyPI** is the standard for Python packages
- **Single package** simplifies installation and version management
- **uv** provides fast installation (recommended)
- **GitHub install** enables testing before release
- **Separate UI** allows using MCP without Node.js

## Alternatives Considered

### Homebrew / apt / winget
- **Pros**: Native package managers
- **Cons**: Complex release process, platform-specific
- **Decision**: Consider for v2

### Docker-only
- **Pros**: Consistent environment
- **Cons**: Overhead, not developer-friendly for local use
- **Decision**: Provide as option, not default

### Monorepo npm package
- **Pros**: Single ecosystem
- **Cons**: Python MCP requires Python anyway
- **Decision**: Rejected

## Consequences

### Positive
- Simple installation: `pip install context-mesh-hub`
- Works with uv for fast installs
- Clear separation: CLI/MCP (Python) vs UI (Node.js)
- Easy updates: `pip install --upgrade context-mesh-hub`

### Trade-offs
- Requires Python 3.12+ on user's system
- UI requires separate Node.js installation
- PyPI release process needed

## Implementation Steps

1. Merge hub-core and hub-cli into single package
2. Update pyproject.toml with proper metadata
3. Test local installation with pip/uv
4. Publish to PyPI (or TestPyPI first)
5. Update README with installation instructions

## Related

- [Decision: Tech Stack](./001-tech-stack.md)
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)

## Status

- **Created**: 2026-01-28
- **Status**: Proposed
