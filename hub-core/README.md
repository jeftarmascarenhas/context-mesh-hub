# Hub Core - Context Mesh Hub MCP Server

Hub Core is the foundational MCP server that reads, validates, and serves Context Mesh artifacts from a repository.

## Features

- **Context Loading**: Indexes and loads all Context Mesh artifacts from `context/` directory
- **Validation**: Validates structure, content sections, and reference integrity
- **Bundling**: Generates deterministic, scoped context bundles (project/feature/decision)
- **MCP Tools**: Exposes agent-agnostic tools for context access

## Installation

### Production Installation

For production use (runtime only):

```bash
cd hub-core
pip install -e .
```

This installs:
- `fastmcp>=2.0.0,<3.0.0` (MCP framework, latest: 2.14.4)

### Development Installation

For development (includes testing tools):

```bash
cd hub-core
pip install -e ".[dev]"
```

This installs:
- `fastmcp>=2.0.0,<3.0.0` (MCP framework, latest: 2.14.4)
- `pytest>=7.4.0` (testing framework)
- `pytest-asyncio>=0.21.0` (async test support)
- `fastmcp[cli]>=2.0.0,<3.0.0` (MCP CLI testing tools)

## Usage

### Configuration

The project includes a `fastmcp.json` configuration file that simplifies running the server with FastMCP CLI tools. This file:
- Defines the server entrypoint (`create_server` function)
- Configures dependencies and editable package installation
- Sets deployment options (transport, logging, etc.)

You can use this configuration file with `mcp dev fastmcp.json` or `mcp run fastmcp.json` commands.

**Note:** For most use cases, simply running `python -m hub_core.server` is the simplest and recommended approach. The FastMCP CLI tools are optional and mainly useful for interactive testing with the MCP Inspector.

### Running in Production

The MCP server can be run directly:

```bash
python -m hub_core.server
```

Or via the entry point (after installation):

```bash
hub-core
```

The server will:
- Auto-detect the repository root (looks for `.git` or `context/` directory)
- Load and index all Context Mesh artifacts
- Expose MCP tools for agent access

**Note:** The server runs as an MCP server and communicates via stdio (for MCP clients like Cursor, Claude Desktop, etc.)

### Running in Development

**Primary Method (Recommended):**

Run the server directly:

```bash
python -m hub_core.server
```

This works without any additional dependencies and is the standard way to run the MCP server.

**Optional: Using FastMCP CLI for Interactive Testing**

For interactive testing with the MCP Inspector, you can use FastMCP's CLI tools:

```bash
# Install dev dependencies first (includes fastmcp[cli])
pip install -e ".[dev]"

# Option 1: Use the configuration file (recommended)
mcp dev fastmcp.json

# Option 2: Use direct file path with editable flag
mcp dev src/hub_core/server.py:create_server -e .
```

**Note:** `fastmcp[cli]` is the package name (installed via `pip install fastmcp[cli]`), but the command you run is `mcp dev`. This is **optional** - it's only needed if you want to use the interactive MCP Inspector for testing. The basic `python -m hub_core.server` command works fine for normal operation.

**Configuration File:** The project includes a `fastmcp.json` configuration file that:
- Specifies the server entrypoint (`create_server` function)
- Configures the environment with editable package installation
- Handles dependencies automatically

This configuration file ensures that the package is installed in editable mode before importing, which fixes relative import issues. You can use it with `mcp dev fastmcp.json` or `mcp run fastmcp.json`.

This starts an interactive CLI session where you can:

1. **List available tools:**
   ```
   list-tools
   ```

2. **Call tools with parameters:**
   ```bash
   # Health check
   call hub_health
   
   # Read project intent
   call context_read artifact_type=project_intent name=
   
   # Validate repository
   call context_validate
   
   # Check prompt pack status
   call hub_prompts_status
   
   # Test template resolution (uses bundled fallback)
   call intent_add_feature feature_name=test-feature inputs='{"what": "Test", "why": "Testing"}'
   
   # Generate project bundle
   call context_bundle bundle_type=project
   ```

3. **Test prompt pack installation** (requires network):
   ```bash
   call hub_prompts_install pack_name=context-mesh-core version=1.1.0 url=https://github.com/jeftarmascarenhas/context-mesh/releases/download/v1.1.0/context-mesh-core-1.1.0.zip
   
   call hub_prompts_use pack_name=context-mesh-core version=1.1.0 source=cached
   
   call hub_prompts_verify pack_name=context-mesh-core version=1.1.0
   ```

**Quick Test Workflow (with MCP Inspector):**

```bash
# 1. Install dependencies (includes fastmcp[cli])
pip install -e ".[dev]"

# 2. Start MCP dev session (from hub-core directory)
# Use the configuration file
mcp dev fastmcp.json

# Or use direct command with editable flag
# mcp dev src/hub_core/server.py:create_server -e .

# 3. In the MCP Inspector session, run quick tests:
call hub_health
call context_validate  
call hub_prompts_status
call intent_add_feature feature_name=test inputs='{"what": "Test feature"}'
```

**Alternative: Test without MCP Inspector**

You can also test the server directly without the interactive CLI:

```bash
# Just run the server - it will start and wait for MCP protocol messages
python -m hub_core.server
```

### Testing

Run unit tests:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_loader.py

# Run with coverage
pytest --cov=hub_core --cov-report=html
```

### Development Workflow

1. **Set up virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Make code changes** in `src/hub_core/`

4. **Run tests**:
   ```bash
   pytest
   ```

5. **Test MCP server**:
   ```bash
   python -m hub_core.server
   ```

### MCP Tools

The server exposes the following tool categories:

#### Chat-First Tools (Recommended for Users)

These are high-level, conversational tools designed for the best chat experience:

**Discovery:**
- `cm_help` - Show available workflows and examples ("What can I do?")
- `cm_status` - Get project status, validation, and guidance ("How's my project?")
- `cm_list_features` - List all features with status
- `cm_list_decisions` - List all decisions (ADRs) with status

**Create (returns ready-to-use markdown):**
- `cm_add_feature` - Add a new feature intent with rendered markdown
- `cm_fix_bug` - Document a bug and prepare for fixing
- `cm_create_decision` - Create a new technical decision (ADR)

**Example usage in chat:**
```
User: "Add a feature for user authentication"
Agent: cm_add_feature(
    name="user-auth",
    what="JWT-based authentication system",
    why="Security is a core requirement",
    acceptance_criteria=["Login works", "Logout works", "Sessions expire"]
)
→ Returns ready markdown to save
```

#### Context Tools
- `context_read` - Read a context artifact (intent, decision, knowledge, etc.)
- `context_validate` - Validate repository structure and content
- `context_bundle` - Generate context bundles (project/feature/decision)
- `hub_health` - Health check and status

#### Prompt Pack Management (Decision 010)
- `hub_prompts_status` - Get current prompt pack status
- `hub_prompts_install` - Install prompt pack from URL
- `hub_prompts_use` - Pin prompt pack version in manifest
- `hub_prompts_verify` - Verify prompt pack integrity

#### Prompt-Driven Intent Tools (Low-Level)
- `intent_new_project` - Create new project setup (uses `new-project.md` template)
- `intent_existing_project` - Bootstrap existing project (uses `existing-project.md` template)
- `intent_add_feature` - Add new feature (uses `add-feature.md` template)
- `intent_update_feature` - Update existing feature (uses `update-feature.md` template)
- `intent_fix_bug` - Fix a bug (uses `fix-bug.md` template)
- `intent_create_agent` - Create new agent (uses `create-agent.md` template)
- `learn_sync` - Sync learnings (uses `learn-update.md` template)

#### Build Protocol Tools
- `build_plan` - Generate build plan from feature intent
- `build_approve` - Approve or reject build plan
- `build_execute` - Generate execution instructions from approved plan

#### Brownfield Tools
- `brownfield_scan` - Scan repository structure
- `brownfield_slice` - Generate context slices
- `brownfield_extract` - Extract context from slices
- `brownfield_report` - Generate comprehensive brownfield analysis

#### Learn Sync Tools
- `learn_sync_initiate` - Start learn sync for a feature
- `learn_sync_review` - Review learning proposals
- `learn_sync_accept` - Accept learning proposals
- `learn_sync_apply` - Apply accepted learnings

## Requirements

### Runtime Requirements
- Python 3.12+
- FastMCP 2.0.0+ (latest: 2.14.4)

### Development Requirements (Optional)
- Python 3.12+
- FastMCP 2.0.0+ with `[cli]` extra (latest: 2.14.4) - **Only needed for interactive MCP Inspector testing**
- pytest 7.4.0+ - **Only needed for running unit tests**
- pytest-asyncio 0.21.0+ - **Only needed for running unit tests**

**Note:** You can run the server with just the runtime requirements. The development dependencies are optional and only needed for:
- Interactive testing with `mcp dev` (requires `fastmcp[cli]`)
- Running unit tests (requires `pytest` and `pytest-asyncio`)

## Architecture

### Core Modules
- `loader.py` - Repository context loader and indexer
- `validator.py` - Validation engine for structure, content, and references
- `bundler.py` - Bundling engine following Decision 003 rules
- `tools.py` - MCP tool definitions
- `server.py` - MCP server entry point

### Prompt Pack Support (Decision 010)
- `prompt_resolver.py` - Template resolution engine (repo override > cached > bundled)
- `prompt_pack_manager.py` - Prompt pack installation, pinning, and verification

### Additional Modules
- `build_protocol.py` - Build governance (Plan / Approve / Execute)
- `brownfield.py` - Brownfield context extraction
- `learn_sync.py` - Learning and evolution synchronization

## Context Mesh Compliance

Hub Core implements:
- Decision 001: Tech Stack (Python 3.12+, FastMCP)
- Decision 002: MCP Tool Contracts
- Decision 003: Context Bundling Strategy
- Decision 010: Prompt Pack Resolution and Update Model

## Configuration

### Repository Root Detection

The server auto-detects the repository root by looking for:
1. `.git` directory (Git repository)
2. `context/` directory (Context Mesh structure)

You can also specify the repository root explicitly:

```bash
python -m hub_core.server /path/to/repo
```

### Prompt Pack Configuration

Prompt packs are configured via `context/hub-manifest.json`:

```json
{
  "promptPack": {
    "name": "context-mesh-core",
    "version": "1.1.0",
    "source": "cached"
  }
}
```

Resolution order (Decision 010):
1. Repo override: `<repoRoot>/.context-mesh/prompts/<template>.md`
2. Cached pack: `~/.context-mesh-hub/prompt-packs/<pack>/<version>/<template>.md`
3. Bundled fallback: `hub-core/prompt-packs/context-mesh-core/1.0.0/<template>.md`

## Troubleshooting

### Server Won't Start

- Check Python version: `python3 --version` (must be >= 3.12)
- Verify FastMCP is installed: `pip list | grep fastmcp`
- Check repository structure: ensure `context/` directory exists

### Templates Not Found

- Verify prompt pack is installed: check `~/.context-mesh-hub/prompt-packs/`
- Check manifest: `cat context/hub-manifest.json`
- Verify bundled fallback exists: `ls hub-core/prompt-packs/context-mesh-core/1.0.0/`

### Import Errors

- Ensure package is installed: `pip install -e .`
- Check Python path: verify `src/` is in Python path
- Use virtual environment to avoid conflicts
