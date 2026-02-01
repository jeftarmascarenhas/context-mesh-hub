# Context Mesh Hub - Evolution Changelog

This changelog records what changed in the Context Mesh Hub project, why it changed, and links to related intents and decisions.

---

## 2026-01-28 - Hub CLI Re-Architecture (Python + AI Agent Selection)

**What Changed:**
- Re-architected Hub CLI from Node.js to Python for stack unification
- Implemented AI agent selection system (`cm init --ai cursor|copilot|gemini|claude`)
- Added persistent configuration in `~/.context-mesh-hub/config.json`
- Created rich terminal UI with Typer + Rich

**New Commands:**
- `cm init --ai <agent>` - Initialize and choose AI backend
- `cm config` - Show MCP configuration for editors
- `cm agents` - List supported AI agents with status
- `cm doctor` - Run diagnostics
- `cm ui` - Start UI dashboard
- `cm` - Interactive menu

**AI Agent Support:**
- **IDE Agents**: Cursor, GitHub Copilot (use MCP in editor)
- **CLI Agents**: Gemini CLI, Claude Code (use `cm chat` in terminal)

**Why:**
- Stack unification: Python for hub-core and hub-cli
- Better integration with FastMCP
- Simpler dependency management
- Inspired by spec-kit's `specify init --ai` pattern
- Clear separation between IDE and CLI agents

**Technical Details:**
- Python 3.12+ with Typer, Rich, httpx, pydantic
- Configuration stored in `~/.context-mesh-hub/`
- Agent detection via `shutil.which()`
- MCP config generation for Cursor, VS Code, Claude Desktop

**Related:**
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Decision: Tech Stack](../decisions/001-tech-stack.md)

---

## 2026-01-28 - Hub UI MCP Client Implementation

**What Changed:**
- Created `hub-ui/src/lib/mcp-client.ts` - MCP client with file system fallback
- Implements all methods required by UI pages:
  - `validate()` - Validate context structure
  - `getProjectIntent()` - Read project-intent.md
  - `getFeatureIntents()` - List all feature-*.md files
  - `getDecisions()` - List all decisions/*.md files
  - `getChangelog()` - Read changelog.md
  - `getPatterns()` / `getAntiPatterns()` - Read knowledge artifacts
  - `getAgents()` - Read agent definitions
  - `callTool(name, params)` - Generic MCP tool interface
  - `getContextSummary()` - Aggregated dashboard data
- File system fallback reads directly from `context/` directory
- Full TypeScript types for ContextArtifact, ValidationResult, MCPError

**Why:**
- Complete the UI implementation (was missing critical piece)
- Enable UI to display context without running MCP server
- Maintain MCP-compatible interface for future HTTP transport
- Support read-only by default (per Decision 006)

**Technical Details:**
- Uses `CONTEXT_MESH_PATH` env var or auto-discovers `context/` directory
- Safe file reading with error handling
- Async/await throughout for performance
- Singleton export for convenience

**Related:**
- [Feature: Hub UI](../intent/feature-hub-ui.md)
- [Decision: UI Read-Only by Default](../decisions/006-ui-readonly-by-default.md)
- [Decision: Tech Stack](../decisions/001-tech-stack.md)

---

## 2026-01-28 - Chat-First MCP Tools Implementation

**What Changed:**
- Added 7 new high-level MCP tools for chat-first experience:
  - `cm_help` - Show available workflows and examples
  - `cm_status` - Get project status with validation and guidance
  - `cm_list_features` - List all features with status
  - `cm_list_decisions` - List all decisions (ADRs) with status
  - `cm_add_feature` - Add feature intent (returns ready markdown)
  - `cm_fix_bug` - Document bug (returns ready markdown)
  - `cm_create_decision` - Create ADR (returns ready markdown)
- Updated README with chat-first tools documentation

**Why:**
- Transform Hub from "MCP API" to "Conversational Interface"
- Enable users to say "add a feature" and get ready-to-use artifacts
- Reduce technical knowledge required to use Hub in chat
- Make MCP "shine" in chat interfaces (Cursor, Claude, Copilot)
- Support the vision of "Operational System of Context"

**Technical Details:**
- Discovery tools return structured guidance
- Create tools render complete markdown (not templates + inputs)
- All tools follow existing naming convention (cm_*)
- Maintains backward compatibility with low-level tools

**Related:**
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Decision: MCP Tool Contracts](../decisions/002-mcp-tool-contracts.md)
- [Decision: Prompt Pack Resolution](../decisions/010-prompt-pack-resolution-and-update-model.md)

---

## 2026-01-27 - Initial Context Mesh Bootstrap

**What Changed:**
- Initialized Context Mesh Hub context scaffolding
- Created required directory structure (`context/knowledge/`, `context/evolution/`)
- Created knowledge placeholders for patterns and anti-patterns
- Fixed broken decision links in all feature intents (6 files corrected)
- Created Decision 009: Context Evolution Rules (was empty, now complete)
- Validated Context Mesh compliance

**Why:**
- Repository bootstrap to establish Context Mesh framework compliance
- Enable future brownfield extraction and feature execution
- Ensure all context artifacts are properly linked and complete

**Related:**
- [Agent: Context Bootstrap](../agents/agent-context-bootstrap.md)
- [Project Intent](../intent/project-intent.md)
- [Decision: Context Evolution Rules](../decisions/009-context-evolution-rules.md)

---

## 2026-01-27 - Feature: Hub Core Implementation

**What Changed:**
- Implemented Hub Core MCP server (Python 3.12+, FastMCP)
- Created repository context loader with safe path validation
- Implemented validation engine (structure, content, references)
- Implemented bundling engine following Decision 003 rules
- Exposed MCP tools: `context_read`, `context_validate`, `context_bundle`, `hub_health`
- Created `hub-core/` Python package with full implementation

**Why:**
- Foundation for Context Mesh Hub runtime
- Enables MCP-based context access for AI agents
- Provides validation and bundling as core capabilities

**Related:**
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Decision: Tech Stack](../decisions/001-tech-stack.md)
- [Decision: MCP Tool Contracts](../decisions/002-mcp-tool-contracts.md)
- [Decision: Context Bundling Strategy](../decisions/003-context-bundling-strategy.md)

---

## 2026-01-27 - Feature: Hub Build Protocol Implementation

**What Changed:**
- Implemented Build Protocol (Plan / Approve / Execute) as extension to Hub Core
- Created `build_protocol.py` with BuildPlan, ApprovalState, ExecutionInstruction classes
- Added MCP tools: `build_plan`, `build_approve`, `build_execute`
- Implemented plan generation from feature intents
- Implemented approval workflow (full/partial/reject)
- Implemented execution instruction generation with approval gating

**Why:**
- Enables governed Build phase execution
- Preserves human authority in AI-assisted development
- Provides structured Plan → Approve → Execute workflow

**Related:**
- [Feature: Hub Build Protocol](../intent/feature-hub-build-protocol.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Decision: Build Execution Modes](../decisions/004-build-execution-modes.md)
- [Decision: MCP Tool Contracts](../decisions/002-mcp-tool-contracts.md)

---

## 2026-01-27 - Feature: Hub Brownfield Implementation

**What Changed:**
- Implemented brownfield context extraction engine
- Created repository scanner for structural analysis
- Implemented context slicing (directory/module/language strategies)
- Implemented four-layer extraction (Structural → Intent → Decisions → Risks)
- Added MCP tools: `brownfield_scan`, `brownfield_slice`, `brownfield_extract`, `brownfield_report`
- All extracted artifacts marked as "PROPOSED" with evidence references

**Why:**
- Enables Context Mesh adoption in existing codebases
- Provides evidence-based context extraction without code modification
- Supports incremental context formalization

**Related:**
- [Feature: Hub Brownfield](../intent/feature-hub-brownfield.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Decision: Brownfield Context Extraction](../decisions/005-brownfield-context-extraction.md)

---

## 2026-01-27 - Feature: Hub CLI Implementation

**What Changed:**
- Implemented Hub CLI as Node.js/TypeScript package
- Created CLI commands: init, start, stop, status, ui, doctor
- Implemented bootstrap (cm init) with template generation
- Implemented runtime management (cm start/stop/status) for MCP server
- Implemented diagnostics (cm doctor) for environment validation
- Created process management utilities (PID tracking, cross-platform spawn)

**Why:**
- Provides developer-friendly entry point for Context Mesh Hub
- Enables fast adoption with familiar CLI workflow
- Centralizes environment diagnostics and troubleshooting

**Related:**
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Decision: Tech Stack](../decisions/001-tech-stack.md)

---

## 2026-01-27 - Feature: Hub UI Implementation

**What Changed:**
- Implemented Hub UI as Next.js v16 application
- Created MCP client with file system fallback (read-only)
- Implemented context visualization pages (intents, decisions, evolution)
- Implemented lifecycle awareness (Intent/Build/Learn indicators)
- Implemented validation feedback display
- Implemented guidance panel for contextual help
- Created navigation and layout structure

**Why:**
- Provides visual dashboard for Context Mesh context
- Enables situational awareness for developers and teams
- Makes context observable and understandable

**Related:**
- [Feature: Hub UI](../intent/feature-hub-ui.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Decision: UI Read-Only by Default](../decisions/006-ui-readonly-by-default.md)
- [Decision: Tech Stack](../decisions/001-tech-stack.md)

---

## 2026-01-27 - Feature: Hub Learn Sync Implementation

**What Changed:**
- Implemented Hub Learn Sync as core module in hub-core
- Created learning data structures (LearningDraft, OutcomeSummary, etc.)
- Implemented outcome collection from build execution
- Implemented learning classification using taxonomy (Decision 008)
- Implemented learning draft generation (6 artifact types)
- Implemented context update proposals (feature intents, decisions, knowledge)
- Implemented changelog entry proposal generation
- Added MCP tools: learn_sync_initiate, learn_sync_review, learn_sync_accept, learn_sync_apply
- Created test suite for learn sync functionality

**Why:**
- Enables explicit learning and context evolution after Build execution
- Prevents loss of insights, mistakes, and refinements
- Creates formal feedback loop in AI-assisted workflows
- Separates execution from learning to avoid bias
- Keeps context accurate as systems evolve

**Related:**
- [Feature: Hub Learn Sync](../intent/feature-hub-learn-sync.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Feature: Hub Build Protocol](../intent/feature-hub-build-protocol.md)
- [Decision: Learning Artifact Taxonomy](../decisions/008-learning-artifact-taxonomy.md)
- [Decision: Context Evolution Rules](../decisions/009-context-evolution-rules.md)

---

## 2026-01-27 - Decision 010: Prompt Pack Resolution and Update Model Implementation

**What Changed:**
- Implemented prompt pack resolution system (Decision 010)
- Created `prompt_resolver.py` with resolution order (repo override > cached > bundled)
- Created `prompt_pack_manager.py` for install/use/verify operations
- Created bundled fallback prompt templates (7 canonical templates: new-project, existing-project, add-feature, update-feature, fix-bug, create-agent, learn-update)
- Added MCP tools for prompt pack management: `hub_prompts_status`, `hub_prompts_install`, `hub_prompts_use`, `hub_prompts_verify`
- Converted intent/build/learn tools to be prompt-driven: `intent_new_project`, `intent_existing_project`, `intent_add_feature`, `intent_update_feature`, `intent_fix_bug`, `intent_create_agent`, `learn_sync`
- Implemented manifest reading/writing for `context/hub-manifest.json`
- Implemented provenance tracking (pack/version/template/hash/source)
- Updated feature intents to reference Decision 010 (hub-core, hub-build-protocol, hub-cli, hub-ui, hub-learn-sync)
- Added missing acceptance criteria to feature-hub-core.md for prompt-driven tools

**Why:**
- Enables deterministic, repeatable context operations across tools
- Provides enterprise-safe customization via repo overrides
- Ensures offline-first behavior with bundled fallback
- Enables decoupled prompt template updates without CLI/MCP upgrades
- Provides governance and auditability (provenance tracking)
- Makes MCP tools prompt-driven as required by Decision 010

**Related:**
- [Decision: Prompt Pack Resolution and Update Model](../decisions/010-prompt-pack-resolution-and-update-model.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Feature: Hub Build Protocol](../intent/feature-hub-build-protocol.md)
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: Hub UI](../intent/feature-hub-ui.md)
- [Feature: Hub Learn Sync](../intent/feature-hub-learn-sync.md)
