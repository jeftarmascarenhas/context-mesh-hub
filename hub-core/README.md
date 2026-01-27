# Hub Core - Context Mesh Hub MCP Server

Hub Core is the foundational MCP server that reads, validates, and serves Context Mesh artifacts from a repository.

## Features

- **Context Loading**: Indexes and loads all Context Mesh artifacts from `context/` directory
- **Validation**: Validates structure, content sections, and reference integrity
- **Bundling**: Generates deterministic, scoped context bundles (project/feature/decision)
- **MCP Tools**: Exposes agent-agnostic tools for context access

## Installation

```bash
cd hub-core
pip install -e .
```

## Usage

### As MCP Server

The server can be run directly:

```bash
python -m hub_core.server
```

Or via the entry point:

```bash
hub-core
```

### MCP Tools

The server exposes the following tools:

- `context_read` - Read a context artifact (intent, decision, knowledge, etc.)
- `context_validate` - Validate repository structure and content
- `context_bundle` - Generate context bundles (project/feature/decision)
- `hub_health` - Health check and status

## Requirements

- Python 3.12+
- FastMCP 0.9.0+

## Architecture

- `loader.py` - Repository context loader and indexer
- `validator.py` - Validation engine for structure, content, and references
- `bundler.py` - Bundling engine following Decision 003 rules
- `tools.py` - MCP tool definitions
- `server.py` - MCP server entry point

## Context Mesh Compliance

Hub Core implements:
- Decision 001: Tech Stack (Python 3.12+, FastMCP)
- Decision 002: MCP Tool Contracts
- Decision 003: Context Bundling Strategy
