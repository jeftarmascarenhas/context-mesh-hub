<div align="center">
    <h1>🌱 Context Mesh Hub</h1>
    <h3><em>Context is Primary. Code is Manifestation.</em></h3>
</div>

<p align="center">
    <strong>One install. CLI + MCP server + UI. Govern AI-assisted development with context-first workflows.</strong>
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

Context Mesh Hub is **3 apps in 1**: a single product that gives you a **CLI**, an **MCP server**, and a **local UI**. Install once and use all three to standardize how your team creates, validates, and evolves **context artifacts** so any AI agent (Cursor, Copilot, Claude, Gemini) can work safely and consistently.

**What you get:**

| Part | What it does |
|------|----------------|
| **CLI (`cm`)** | Interactive setup, MCP config, slash-command install, diagnostics, UI launcher |
| **MCP server** | Runs inside your editor; exposes tools for context (intents, decisions, status, add feature, etc.) |
| **UI** | Local dashboard to browse intents, decisions, and validation (`cm ui`) |

**Workflow:** Intent → Build → Learn. Context lives in your repo (`context/`); the MCP server is the single authority gate; agents are operators, not authorities.

## ⚡ Get Started

### 1. Install Context Mesh Hub (one install, all three parts)

Use [uv](https://docs.astral.sh/uv/) to install the CLI. The MCP server is included; the UI runs via `cm ui` when needed.

#### Quick Install (recommended)

```bash
# Install + run setup in one command
uv tool install context-mesh-hub-cli --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli && cm
```

> If `cm` is not found, add `~/.local/bin` to your PATH: `export PATH="$HOME/.local/bin:$PATH"`

The interactive menu will guide you through:
- 🔌 Get MCP config for your editor (Cursor, Copilot, Claude, Gemini)
- ⚡ Install slash commands (`/add-feature`, `/fix-bug`, etc.)
- 🎯 Install Context Mesh Skill for Cursor/Copilot
- 🔍 Run diagnostics
- 📋 List AI agents

#### Advanced Options

**Install only (run `cm` later):**

```bash
uv tool install context-mesh-hub-cli --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli
```

**One-time run (no install):**

```bash
uvx --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli cm --help
```

**From source (development):**

```bash
git clone https://github.com/jeftarmascarenhas/context-mesh-hub.git
cd context-mesh-hub
./install.sh
source .venv/bin/activate   # if using venv
```

**Upgrade:**

```bash
uv tool upgrade context-mesh-hub-cli
```

**Uninstall:**

```bash
uv tool uninstall context-mesh-hub-cli
```

### 2. Set up your project

Run:

```bash
cm init
```

Then choose with the arrow keys:

- **Get MCP config** – get editor-specific JSON for Cursor, Copilot, Claude, or Gemini
- **Install slash commands** – install `/cm-add-feature`, `/cm-build`, etc. into your agent's command folder
- **Install Context Mesh Skill** – install AI agent skill for better context understanding
- **Run diagnostics**, **List AI agents**, or **Exit**

### 3. Configure MCP in your editor

Run:

```bash
cm config
```

If you don’t pass `--editor`, you’ll be asked to pick your editor. Copy the JSON and add it to:

- **Cursor:** Settings → Features → MCP Servers  
- **VS Code + Copilot:** Settings → GitHub Copilot → MCP  
- **Claude Desktop:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### 4. Install slash commands (optional, for agent chat)

So that your AI assistant can use commands like `/cm-add-feature` and `/cm-status`:

```bash
cm setup-commands
```

Pick your agent (Cursor, Copilot, Claude, Gemini). Commands are written to the right place (e.g. `.cursor/commands/` for Cursor).

### 5. Use Context Mesh in your editor

- **Via MCP:** In chat, use the Context Mesh Hub tools (e.g. `cm_status`, `cm_help`, `cm_add_feature`).
- **Via slash commands:** Type `/` and choose a command (e.g. `/cm-add-feature`, `/cm-status`).

## 🤖 Supported AI Agents

| Agent | Type | Support | Notes |
|-------|------|---------|-------|
| [Cursor](https://cursor.sh/) | IDE | ✅ | MCP + slash commands in chat |
| [GitHub Copilot](https://github.com/features/copilot) | IDE | ✅ | MCP in VS Code; slash commands in `.github/prompts/` |
| [Claude Desktop](https://claude.ai/download) | IDE | ✅ | MCP + slash commands |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | CLI | ✅ | MCP + slash commands (TOML) |

## 🔧 CLI Reference

| Command | Description |
|---------|-------------|
| `cm` | Same as `cm init` (interactive setup menu) |
| `cm init` | Interactive setup: register project, MCP config, slash commands, UI, diagnostics, agents |
| `cm config` | Get MCP config (interactive editor choice, or `--editor cursor\|copilot\|claude\|gemini`) |
| `cm config --raw` | Print only the JSON (use with `--editor` to skip prompt) |
| `cm setup-commands` | Install slash commands (interactive, or `--agent cursor\|copilot\|claude\|gemini`) |
| `cm doctor` | Run diagnostics and check environment |
| `cm agents` | List supported agents and status |
| `cm projects list` | List registered Context Mesh projects |
| `cm projects add [path]` | Register a project (default: current directory) |
| `cm projects remove [path]` | Unregister a project |

**Examples:**

```bash
cm init                     # Interactive setup (recommended)
cm                          # Same as cm init
cm config --editor cursor   # MCP JSON for Cursor
cm setup-commands --agent cursor
cm doctor
cm ui
```

**MCP tools (after configuring MCP):** `cm_help`, `cm_status`, `cm_list_features`, `cm_list_decisions`, `cm_add_feature`, `cm_fix_bug`, `cm_create_decision`, and more.

## 📚 Core Philosophy

- **Context is primary** – Code is its manifestation.  
- **Local-first** – No cloud required; no login.  
- **Repo-first** – All artifacts in `context/`, versioned with Git.  
- **MCP-first** – AI agents interact via the Model Context Protocol.  
- **Agents are operators** – Human approval required; MCP is the authority gate.

**Workflow:** Intent → Build → Learn (define what and why, execute with governance, formalize learnings).

## 🔧 Prerequisites

- **Python 3.12+**
- **uv** for install ([install uv](https://docs.astral.sh/uv/))
- **Git**
- A supported AI editor (Cursor, VS Code + Copilot, Claude Desktop, or Gemini CLI)

## 📖 Learn More

- **[Context Mesh Framework](https://github.com/jeftarmascarenhas/context-mesh)** – Methodology behind the Hub
- **[AGENTS.md Standard](https://agents.md/)** – AI agent instructions standard
- **[Model Context Protocol](https://modelcontextprotocol.io/)** – MCP specification

## Repository structure

```
context-mesh-hub/
├── README.md           # This file
├── install.sh          # Dev install (CLI + MCP from source)
├── hub-cli/            # CLI (cm) — install this for "one install"
├── hub-core/           # MCP server (used by CLI and editors)
└── context/            # In your project: intent, decisions, knowledge, agents, evolution
```

**Component READMEs:** [hub-cli/README.md](hub-cli/README.md) | [hub-core/README.md](hub-core/README.md)

## 👥 Maintainers

- Jeftar Mascarenhas ([@jeftarmascarenhas](https://github.com/jeftarmascarenhas))

## 💬 Support

Open a [GitHub issue](https://github.com/jeftarmascarenhas/context-mesh-hub/issues/new) for support.

## 📄 License

MIT License.
