<div align="center">
    <h1>Context Mesh Hub</h1>
    <h3>Keep your AI assistants context-aware across sessions, team members, and tool changes.</h3>
</div>

<p align="center">
    <strong>CLI + MCP Server in one install. Standardize how your team collaborates with AI.</strong>
</p>

<p align="center">
    <a href="https://github.com/jeftarmascarenhas/context-mesh-hub/stargazers"><img src="https://img.shields.io/github/stars/jeftarmascarenhas/context-mesh-hub?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/jeftarmascarenhas/context-mesh-hub/blob/main/LICENSE"><img src="https://img.shields.io/github/license/jeftarmascarenhas/context-mesh-hub" alt="License"/></a>
</p>

---

## The Problem

AI coding assistants work great for individual conversations but lose context between sessions. When team members ask the same AI different questions, they get inconsistent answers. When you switch tools or restart conversations, your AI forgets your project's patterns, decisions, and conventions.

## The Solution

Context Mesh Hub provides a **CLI** and **MCP Server** (connects to your AI editor) to maintain consistent project context. Your team's intents, decisions, and patterns live in your repository (`context/` directory) and stay accessible to any AI agent.

**What you get:**

| Component | Purpose |
|-----------|----------|
| **CLI (`cm`)** | Interactive setup, configuration generation, and project management |
| **MCP Server** | Runs in your editor, gives AI access to project context and tools |

**How it works:** Your project documentation lives in `context/` directory. The MCP server makes this available to AI assistants (Cursor, Copilot, Claude, Gemini) so they give consistent, context-aware responses.

## Quick Start

### Install and Setup

Requires: [uv](https://docs.astral.sh/uv/), Python 3.12+, Git

```bash
# Install + run interactive setup
uv tool install context-mesh-hub-cli --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli && cm
```

> **Note:** If `cm` command not found, add `~/.local/bin` to your PATH

The setup will:
1. Generate MCP configuration for your editor
2. Create instruction files for your AI assistant  
3. Set up project context structure

<details>
<summary><strong>Other Installation Options</strong></summary>

**Install only (run setup later):**
```bash
uv tool install context-mesh-hub-cli --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli
```

**One-time use:**
```bash
uvx --from git+https://github.com/jeftarmascarenhas/context-mesh-hub.git#subdirectory=hub-cli cm
```

**From source:**
```bash
git clone https://github.com/jeftarmascarenhas/context-mesh-hub.git
cd context-mesh-hub && ./install.sh
```

**Upgrade:**
```bash
uv tool upgrade context-mesh-hub-cli
```
</details>

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

## Supported AI Agents

| Editor/Agent | Support | Notes |
|--------------|---------|-------|
| [Cursor](https://cursor.sh/) | Full | MCP + slash commands |
| [GitHub Copilot](https://github.com/features/copilot) (VS Code) | Full | MCP + always-on instructions |
| [Claude Desktop](https://claude.ai/download) | Full | MCP + slash commands |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Full | MCP + TOML commands |

## CLI Commands

| Command | Description |
|---------|-------------|
| `cm` | Interactive setup menu |
| `cm config --editor <name>` | Generate MCP config for your editor |
| `cm setup-commands --agent <name>` | Install AI assistant instructions |
| `cm doctor` | Check environment and configuration |

**MCP Tools** (available in your AI after setup): `cm_status`, `cm_add_feature`, `cm_create_decision`, `cm_list_features`, `cm_help`

## Context Mesh Skills

Skills provide your AI with deep understanding of Context Mesh workflows and your project's specific patterns.

### Install Skills

```bash
cm skills install
```

### What Skills Provide

**Enhanced AI Understanding:**
- Deep knowledge of Intent → Build → Learn workflow
- Specialized prompts for feature planning and decision-making
- Understanding of your project's established patterns and anti-patterns
- Automatic adherence to documented conventions and decisions

**Installation Locations:**
- **Cursor:** `.cursor/docs/` directory with comprehensive workflow documentation
- **VS Code + Copilot:** Enhanced instructions in `.github/copilot-instructions.md` 
- **Claude/Others:** Agent-specific skill directories with relevant documentation

**Benefits:**
- AI suggests features that align with project architecture
- Automatic reference to existing decisions when making new ones
- Consistent code patterns across team members
- Better understanding of project context and constraints

## How It Works

**Local-first:** Everything lives in your Git repository (`context/` directory). No cloud services or accounts required.

**Workflow:** Document your intents and decisions → AI implements following your patterns → Capture learnings back into documentation.

**Governance:** AI assistants are operators that follow your project's established context, not autonomous decision-makers.

## Learn More

- [Context Mesh Framework](https://github.com/jeftarmascarenhas/context-mesh) – Methodology and principles
- [Model Context Protocol](https://modelcontextprotocol.io/) – Technical specification
- [AGENTS.md](AGENTS.md) – Instructions for AI agents working with this project

## Support

**Issues:** [GitHub Issues](https://github.com/jeftarmascarenhas/context-mesh-hub/issues/new)  
**Maintainer:** [Jeftar Mascarenhas](https://github.com/jeftarmascarenhas)  
**License:** MIT
