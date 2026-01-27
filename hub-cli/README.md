# Hub CLI - Context Mesh Hub Command Line Interface

The CLI provides bootstrap, runtime management, and diagnostics for Context Mesh Hub.

## Installation

```bash
cd hub-cli
pnpm install
pnpm build
```

## Usage

### Initialize Context Mesh Hub

```bash
cm init
```

Initializes Context Mesh Hub in the current repository. Creates required directory structure and template files.

### Start MCP Server

```bash
cm start
```

Starts the local MCP server for the current repository.

### Check Status

```bash
cm status
```

Reports whether the MCP server is running.

### Stop MCP Server

```bash
cm stop
```

Stops the local MCP server.

### Launch UI

```bash
cm ui
```

Launches the local Next.js UI (when Feature 5 is complete).

### Diagnostics

```bash
cm doctor
```

Runs diagnostics to check environment, versions, and repository structure.

## Commands

- `cm init` - Initialize Context Mesh Hub
- `cm start` - Start MCP server
- `cm stop` - Stop MCP server
- `cm status` - Check MCP server status
- `cm ui` - Launch local UI
- `cm doctor` - Run diagnostics

## Requirements

- Node.js 20+ (Active LTS)
- Python 3.12+
- pnpm (package manager)

## Architecture

The CLI is a thin orchestration layer that:
- Delegates domain logic to the MCP server
- Manages process lifecycle
- Provides developer-friendly commands
- Does not implement context logic itself
