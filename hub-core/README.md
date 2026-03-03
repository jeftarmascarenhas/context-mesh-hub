# Hub Core — Context Mesh Hub MCP Server

The **MCP server** part of Context Mesh Hub. It reads, validates, and serves Context Mesh artifacts from a repo. Editors (Cursor, Copilot, Claude, Gemini) talk to it via the Model Context Protocol.

**→ Install and Get Started:** See the [root README](../README.md). The MCP server is installed automatically when you install the CLI.

---

## What this package is

- **Runtime:** MCP server used by the CLI and by AI editors
- **No standalone install for end users** — install Context Mesh Hub from the root; hub-core is a dependency of hub-cli

## Features

- **Context loading** – Index and load artifacts from `context/`
- **Validation** – Structure, content, and reference checks
- **Bundling** – Scoped context bundles (project/feature/decision)
- **MCP tools** – `cm_help`, `cm_status`, `cm_add_feature`, `cm_list_features`, `cm_list_decisions`, and more

## Usage (for end users)

You don’t run hub-core directly. You:

1. Install Context Mesh Hub from the root (CLI install pulls in hub-core)
2. Run `cm config` and add the JSON to your editor’s MCP settings
3. Use Context Mesh tools from your editor’s chat

## Development

### Install

```bash
cd hub-core
pip install -e .        # runtime
pip install -e ".[dev]" # + tests, MCP Inspector
```

### Run server

```bash
python -m hub_core.server
```

Or with FastMCP config (optional):

```bash
mcp dev fastmcp.json
```

### Test

```bash
pytest
```

### Main modules

- `loader.py` – Repo context loader and indexer
- `validator.py` – Validation engine
- `bundler.py` – Context bundling (Decision 003)
- `tools.py` – MCP tool definitions
- `server.py` – MCP server entry point
- `prompt_resolver.py` / `prompt_pack_manager.py` – Prompt packs (Decision 010)

## Requirements

- Python 3.12+
- FastMCP 2.x

## License

MIT
