<div align="center">
    <h1>🌱 Context Mesh Hub</h1>
    <h3><em>Context is Primary. Code is Manifestation.</em></h3>
</div>

<p align="center">
    <strong>An open source framework that standardizes Context Engineering processes for AI-assisted development.</strong>
</p>

<p align="center">
    <a href="https://github.com/jeftarmascarenhas/context-mesh-hub/stargazers"><img src="https://img.shields.io/github/stars/jeftarmascarenhas/context-mesh-hub?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/jeftarmascarenhas/context-mesh-hub/blob/main/LICENSE"><img src="https://img.shields.io/github/license/jeftarmascarenhas/context-mesh-hub" alt="License"/></a>
</p>

---

## Table of Contents

- [🤔 What is Context Mesh Hub?](#-what-is-context-mesh-hub)
- [⚡ Get Started](#-get-started)
- [🤖 Supported AI Agents](#-supported-ai-agents)
- [🔧 CLI Reference](#-cli-reference)
- [📚 Core Philosophy](#-core-philosophy)
- [🔧 Prerequisites](#-prerequisites)
- [📖 Learn More](#-learn-more)
- [👥 Maintainers](#-maintainers)
- [📄 License](#-license)

## 🤔 What is Context Mesh Hub?

Context Mesh Hub is a **local-first, repo-first, MCP-first** system that turns AI-assisted development into a **governed, repeatable process**.

It standardizes how teams create, validate, execute, and evolve **context artifacts** so any AI agent (Cursor, Copilot, Claude, etc.) can operate safely and consistently.

**Key differences from other tools:**

| Feature | Context Mesh Hub | spec-kit |
|---------|------------------|----------|
| Focus | Context Strategy Management | Spec-Driven Development |
| Interface | **MCP** (in editor) + CLI | CLI + Slash Commands |
| Output | Context artifacts | Code from specs |
| Workflow | Intent → Build → Learn | Specify → Plan → Implement |

## ⚡ Get Started

### 1. Install Context Mesh Hub CLI

Choose your preferred installation method:

#### Option 1: Persistent Installation (Recommended)

Install once and use everywhere with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install context-mesh-hub-cli --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli
```

> **Note**: If `cm` is not found, add `~/.local/bin` to your PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

Then use the tool directly:

```bash
# Initialize with your AI agent
cm init --ai cursor

# Get MCP configuration
cm config

# Check installed agents
cm agents

# Run diagnostics
cm doctor
```

To upgrade:

```bash
uv tool install context-mesh-hub-cli --force --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli
```

To uninstall:

```bash
uv tool uninstall context-mesh-hub-cli
```

#### Option 2: One-time Usage

Run directly without installing:

```bash
uvx --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli cm --help
```

#### Option 3: Development Installation

Clone and install for development:

```bash
git clone https://github.com/jeftarmascarenhas/context-mesh-hub.git
cd context-mesh-hub
./install.sh
source .venv/bin/activate
```

**Benefits of persistent installation:**

- Tool stays installed and available in PATH
- No need to clone repositories
- Better tool management with `uv tool list`, `uv tool upgrade`, `uv tool uninstall`
- Cleaner shell configuration

### 2. Initialize with your AI agent

```bash
cm init --ai cursor      # For Cursor IDE
cm init --ai copilot     # For VS Code + GitHub Copilot
cm init --ai gemini      # For Gemini CLI
cm init --ai claude      # For Claude Code
```

### 3. Configure MCP in your editor

```bash
cm config
```

Copy the JSON output and paste it in your editor's MCP settings:

- **Cursor**: Settings → Features → MCP Servers
- **VS Code + Copilot**: Settings → GitHub Copilot → MCP
- **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### 4. Use Context Mesh in your AI editor

Once MCP is configured, you can use Context Mesh tools directly in your editor's chat:

```
@context-mesh-hub cm_status
@context-mesh-hub cm_help
@context-mesh-hub cm_add_feature
```

## 🤖 Supported AI Agents

| Agent | Type | Support | Notes |
|-------|------|---------|-------|
| [Cursor](https://cursor.sh/) | IDE | ✅ | MCP in editor chat |
| [GitHub Copilot](https://github.com/features/copilot) | IDE | ✅ | MCP in VS Code |
| [Claude Desktop](https://claude.ai/download) | IDE | ✅ | MCP in desktop app |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | CLI | ✅ | Terminal chat |
| [Claude Code](https://www.anthropic.com/claude-code) | CLI | ✅ | Terminal chat |

## 🔧 CLI Reference

The `cm` command supports the following options:

### Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize Context Mesh Hub with your preferred AI agent |
| `config` | Show MCP configuration for AI editors |
| `agents` | List supported AI agents and their status |
| `doctor` | Run diagnostics and check environment |
| `ui` | Start the UI dashboard |
| `chat` | Chat with Context Mesh Hub (requires CLI agent) |

### `cm init` Options

| Option | Description |
|--------|-------------|
| `--ai` | AI agent to use: `cursor`, `copilot`, `gemini`, `claude` |

### Examples

```bash
# Initialize with Cursor
cm init --ai cursor

# Initialize with GitHub Copilot
cm init --ai copilot

# Show MCP configuration
cm config

# List agents and status
cm agents

# Run diagnostics
cm doctor

# Start UI dashboard
cm ui
```

### MCP Tools Available

After configuring MCP, these tools are available in your editor:

| Tool | Description |
|------|-------------|
| `cm_help` | Show available workflows and examples |
| `cm_status` | Get project status with validation |
| `cm_list_features` | List all features with status |
| `cm_list_decisions` | List all decisions (ADRs) |
| `cm_add_feature` | Add a new feature intent |
| `cm_fix_bug` | Create a bug fix intent |
| `cm_create_decision` | Create a new decision (ADR) |

## 📚 Core Philosophy

Context Mesh Hub follows the **Intent → Build → Learn** workflow:

1. **Intent**: Define WHAT and WHY (feature intents + acceptance criteria)
2. **Build**: Execute with governance (Plan → Approve → Execute)
3. **Learn**: Formalize outcomes into reusable knowledge

**Key principles:**

- **Context is primary** - Code is its manifestation
- **Local-first** - No cloud dependencies, no login required
- **Repo-first** - All artifacts in `context/` directory, versioned with Git
- **MCP-first** - AI agents interact via Model Context Protocol
- **Agents are operators, not authorities** - Human approval required

## 🔧 Prerequisites

- **Python 3.12+**
- **uv** for package management ([install](https://docs.astral.sh/uv/))
- **Git**
- Supported AI editor (Cursor, VS Code + Copilot, Claude Desktop)

## 📖 Learn More

- **[Context Mesh Framework](https://github.com/jeftarmascarenhas/context-mesh)** - The underlying methodology
- **[AGENTS.md Standard](https://agents.md/)** - AI agent instructions standard
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP specification

## Repository Structure

```
context/
├── intent/
│   ├── project-intent.md
│   └── feature-*.md
├── decisions/
│   └── 001-*.md
├── knowledge/
│   ├── patterns/
│   └── anti-patterns/
├── agents/
│   └── agent-*.md
└── evolution/
    └── changelog.md
```

## 👥 Maintainers

- Jeftar Mascarenhas ([@jeftarmascarenhas](https://github.com/jeftarmascarenhas))

## 💬 Support

For support, please open a [GitHub issue](https://github.com/jeftarmascarenhas/context-mesh-hub/issues/new).

## 📄 License

This project is licensed under the terms of the MIT open source license.
