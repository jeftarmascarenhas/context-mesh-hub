# Context Mesh Hub CLI

The **CLI** part of Context Mesh Hub — one of two components (CLI + MCP server). Install Context Mesh Hub from the **root repo**; the CLI (`cm`) is the main entry point.

**→ Install and Get Started:** See the [root README](../README.md).

---

## What this package is

- **`cm`** / **`cm init`** – Interactive setup menu (register project, MCP config, slash commands, doctor, agents)
- **MCP server** – Installed with the CLI (hub-core); editors talk to it via MCP

You do **not** install hub-cli alone for normal use. Use the root install so you get CLI + MCP in one go.

## Installation (from root)

```bash
# Persistent install (recommended)
uv tool install context-mesh-hub-cli --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli
```

Or from source:

```bash
git clone https://github.com/jeftarmascarenhas/context-mesh-hub.git
cd context-mesh-hub
./install.sh
source .venv/bin/activate   # if using venv
```

## Quick reference

| Command | Description |
|--------|-------------|
| `cm` | Same as `cm init` (interactive setup) |
| `cm init` | Interactive setup: register project, MCP config, slash commands, UI, doctor, agents |
| `cm config` | Get MCP config (interactive or `--editor cursor\|copilot\|claude\|gemini`) |
| `cm config --raw` | Print only JSON (use with `--editor`) |
| `cm setup-commands` | Install slash commands (interactive or `--agent cursor\|copilot\|claude\|gemini`) |
| `cm doctor` | Run diagnostics |
| `cm ui` | Start the local UI |
| `cm agents` | List supported agents |
| `cm projects list` | List registered projects |
| `cm projects add [path]` | Register a project (default: current dir) |
| `cm projects remove [path]` | Unregister a project |

Slash commands (`/cm-add-feature`, `/cm-build`, etc.) are **not** run from the CLI. They are installed into your AI agent’s chat via `cm setup-commands` (e.g. Cursor → `.cursor/commands/`).

## MCP configuration

Each editor uses a different JSON shape. Use `cm config` (interactive) or `cm config --editor cursor` (or `copilot`, `claude`, `gemini`) to get the right JSON.

- **Cursor / Claude / Gemini:** `mcpServers`
- **VS Code GitHub Copilot:** `servers` (use `cm config --editor copilot`)

## Development

```bash
cd hub-cli
uv sync
uv run cm
uv run pytest
uv build
```

## Requirements

- Python 3.12+
- uv (recommended) or pip
- Node.js 20+ only if you run `cm ui`

## License

MIT
