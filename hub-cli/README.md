# Context Mesh Hub CLI

**Framework that standardizes Context Engineering processes**

The CLI provides setup, configuration, and natural language interaction with Context Mesh Hub.

## Installation

### With uv (recommended)

```bash
uv tool install context-mesh-hub
```

### With pip

```bash
pip install context-mesh-hub
```

### From source (development)

```bash
cd hub-cli
uv sync
uv run cm
```

## Usage

### Interactive Setup

Run without arguments to start the interactive setup:

```bash
cm
```

This will:
1. Check your environment (Python, dependencies)
2. Show the MCP configuration to copy to your AI editor
3. Provide options to start UI, run diagnostics, or chat

### Commands

| Command | Description |
|---------|-------------|
| `cm` | Interactive setup and menu |
| `cm config` | Show MCP configuration for AI editors |
| `cm doctor` | Run diagnostics and check environment |
| `cm ui` | Start the UI dashboard |
| `cm chat` | Chat with natural language |
| `cm chat "message"` | Execute a natural language command |

### Natural Language Chat

The CLI supports natural language commands when an LLM API key is configured:

```bash
# Interactive chat
cm chat

# Single command
cm chat "add a feature for user authentication"
cm chat "what features do we have?"
cm chat "show project status"
```

### LLM Configuration

Set environment variables to enable natural language:

```bash
# OpenAI (default)
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
export CM_LLM_PROVIDER=anthropic

# Ollama (local, no API key needed)
export CM_LLM_PROVIDER=ollama
export CM_LLM_MODEL=llama3.2

# OpenRouter
export OPENROUTER_API_KEY=sk-or-...
export CM_LLM_PROVIDER=openrouter
```

## MCP Configuration

After running `cm` or `cm config`, copy the JSON configuration to your AI editor:

### Cursor

Settings → Features → MCP Servers → Add

### VS Code + GitHub Copilot

Settings → GitHub Copilot → MCP Servers

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "context-mesh-hub": {
      "command": "python",
      "args": ["-m", "hub_core.server"]
    }
  }
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                    │
│                                                                 │
│   ┌─────────────┐              ┌─────────────────────────────┐ │
│   │   CLI (cm)  │              │  Chat (Cursor/Copilot/etc)  │ │
│   │  Python+uv  │              │                             │ │
│   └──────┬──────┘              └──────────────┬──────────────┘ │
│          │                                    │                 │
│          ▼                                    ▼                 │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │                    MCP SERVER (hub-core)                 │ │
│   │                     Python + FastMCP                     │ │
│   └──────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                         │
│                    │  context/ files │                         │
│                    │  (repo-first)   │                         │
│                    └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

## Development

```bash
cd hub-cli

# Install dependencies
uv sync

# Run in development
uv run cm

# Run tests
uv run pytest

# Build
uv build
```

## Requirements

- Python 3.12+
- uv (recommended) or pip
- Node.js 20+ (for UI only)

## License

MIT
