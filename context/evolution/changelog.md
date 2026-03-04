# Context Mesh Hub - Evolution Changelog

This changelog records what changed in the Context Mesh Hub project, why it changed, and links to related intents and decisions.

---

## 2026-03-04 - Hub-Core Architecture Refactoring Completed (F006)

**What Changed:**
- Completed 5-phase refactoring of hub-core from 5,034 lines (73% problematic) to clean 3-layer architecture
- Created 28 new files totaling ~6,000 lines of well-structured, testable code
- Removed 4 legacy files totaling 3,673 lines (tools.py, brownfield.py, build_protocol.py, learn_sync.py)
- Implemented file-based persistence for BuildPlans and LearningProposals in `.context-mesh/`
- Achieved zero breaking changes - all MCP tools maintain exact same interface
- Updated test_learn_sync.py to use new LearnService architecture

**Implementation Timeline:**
- **Phase 1 (Foundation)**: Created `shared/`, `domain/models/` with custom exceptions and dataclasses
- **Phase 2 (Infrastructure)**: Built 12 files including parsers, persistence, and scanner modules
- **Phase 3 (Domain Services)**: Created 4 services (Intent, Build, Analysis, Learn) totaling 2,063 lines
- **Phase 4 (MCP Tools)**: Split tools.py into 8 focused files + decorators for error handling
- **Phase 5 (Cleanup)**: Removed legacy code, fixed imports, updated server.py with DI

**Outcomes:**
- ✅ **Maintainability**: All files now <650 lines (largest: intent_service.py at 645 lines)
- ✅ **Architecture**: Clear separation of Domain/Infrastructure/MCP layers
- ✅ **Persistence**: BuildPlans and LearningProposals survive server restarts
- ✅ **Testability**: Domain services are pure functions, easy to test with mocks
- ✅ **Error Handling**: Consistent custom exceptions throughout codebase
- ✅ **Dependency Injection**: All services receive dependencies via constructor
- ⏳ **Test Coverage**: Basic tests updated, comprehensive 70%+ coverage pending (Phase 6)

**Technical Details:**
- Domain: `intent_service.py` (645), `build_service.py` (469), `analysis_service.py` (388), `learn_service.py` (561)
- Infrastructure: 12 files across parsers/, persistence/, scanner/ (~1,427 lines)
- MCP: 8 tools + decorators.py, server.py (229 lines with DI setup)
- Shared: errors.py (7 custom exceptions), config.py, utils.py

**Learnings:**
- Phased approach allowed incremental validation without breaking existing functionality
- DI pattern dramatically improved testability - services can now be tested in isolation
- File-based persistence is sufficient for v1 (no database needed)
- Splitting tools.py into focused files revealed hidden coupling and duplication
- Import path issues (... vs ..) caused initial syntax errors - resolved systematically

**Process Violation (Meta-learning):**
- ⚠️ Initially created `REFACTORING_PLAN.md` outside Context Mesh structure
- Corrected by creating proper feature intent `F006-refactor-hub-core-architecture.md`
- Lesson: Even when building Context Mesh Hub, FOLLOW Context Mesh (Intent → Build → Learn)

**Related:**
- Feature: [F006 - Refactor Hub-Core Architecture](../intent/F006-refactor-hub-core-architecture.md)
- Decision: [D001 - Tech Stack](../decisions/D001-tech-stack.md)
- Feature: [F004 - Hub Core](../intent/F004-hub-core.md)

**Next Steps:**
- Complete Phase 6: Comprehensive test suite with 70%+ coverage
- Create ARCHITECTURE.md documenting layer responsibilities
- Use learn_sync MCP to formalize additional learnings

---

## 2026-03-03 - Hub-Core Architecture Refactoring Analysis (D001)

**What Changed:**
- Comprehensive analysis of hub-core identified critical code smells and architectural issues
- Created Decision D001 documenting complete refactoring strategy with 3-layer architecture
- Documented all problems: God Objects, in-memory state, coupling, parsing duplication

**Why:**
- Current hub-core violates FastMCP best practices and software engineering principles
- tools.py with 2047 lines is unmaintainable (God Object)
- build_protocol.py and learn_sync.py lose state on restart (no persistence)
- brownfield.py with 665 lines mixes multiple responsibilities
- Lack of tests (~10% coverage), difficult to maintain and evolve

**Related:**
- Decision: D001
- Feature: F006 (created retroactively on 2026-03-04)

**Next Steps:**
- Execute refactoring (completed 2026-03-04)

---

## 2026-03-03 - Brownfield Extraction Artifact Classification Fix (D014)

**What Changed:**
- Refactored `hub-core/src/hub_core/brownfield.py` to correctly classify artifacts per Context Mesh 1.1.0
- Removed automatic "Feature Intent" generation for entry points (main.py, server.py, etc.)
- Changed structural analysis to propose "Decisions" about architecture instead of "Features"
- Focused intent reconstruction on value-delivering capabilities, not implementation files

**Why:**
- Previous implementation violated Context Mesh 1.1.0 principles
- Was generating dozens of meaningless "Feature: main" proposals
- Confused "WHAT provides value" (Features) with "HOW it's implemented" (Decisions)
- Created noise that made brownfield extraction unusable

**Technical Details:**
- `_extract_structural_discovery()` now creates "decision" artifacts about architecture
- `_extract_intent_reconstruction()` no longer creates features for entry points
- Features should only be proposed for user/system-facing capabilities
- Decisions proposed for tech stack, frameworks, dependency management, build tools

**Correct Classification:**
- **Features**: User Authentication, Todo CRUD, Build Protocol (value to users/system)
- **Decisions**: Tech Stack, Framework Choice, Database Selection (technical choices)
- **Patterns**: API design, error handling approaches (reusable code patterns)
- **Knowledge**: Domain rules, constraints, integration requirements

**Related:**
- [Decision: D014 Brownfield Extraction Artifact Classification](../decisions/D014-brownfield-extraction-artifact-classification.md)
- [Decision: D005 Brownfield Context Extraction](../decisions/D005-brownfield-context-extraction.md)
- [Decision: D013 MCP Simplification](../decisions/D013-mcp-simplification.md)
- [Feature: Hub Brownfield](../intent/F001-hub-brownfield.md)

---

## 2026-03-03 - MCP Simplification (D013)

**What Changed:**
- Refactored MCP from 43 tools to 8 consolidated tools:
  - `cm_init` - Project initialization (new, existing, migrate)
  - `cm_intent` - Intent management (features, decisions, bugs)
  - `cm_agent` - Agent management (CRUD operations)
  - `cm_build` - Build protocol (bundle, plan, approve, execute)
  - `cm_validate` - Context validation
  - `cm_analyze` - Brownfield analysis (scan, slice, extract, report)
  - `cm_learn` - Learning sync (initiate, review, accept, apply)
  - `cm_status` - Complete project status

- Created Context Mesh Skill (`.github/skills/context-mesh/`):
  - SKILL.md with pushy description for better triggering
  - Reference guides: workflow, brownfield, nomenclature, parallelization
  
- Updated CLI and slash commands for new tools:
  - Backward compatibility via tool migration mapping
  - Updated all command templates to reference new tools

- Introduced standardized nomenclature:
  - Features: `F001-name.md`, `F002-name.md`
  - Decisions: `D001-name.md`, `D002-name.md`
  - Migration support via `cm_init(action="migrate")`

**Why:**
- 43 tools created cognitive overload for AI agents
- Redundancy between similar tools (e.g., `cm_add_feature` vs `intent_add_feature`)
- "The intelligence is in the Skill, not the MCP" - MCP should be CRUD + optimized reading
- Context Mesh is a documentation framework, not a complex orchestration system
- Standardized nomenclature enables cross-references (F001 → D001)

**Technical Details:**
- Tools now use action/type pattern: `cm_intent(action="create", type="feature")`
- Old tool names work via deprecation mapping in CLI
- Skill provides workflow guidance, brownfield is a workflow not tools
- Parallelization support via sub-agents documented in skill

**Related:**
- [Decision: D013 MCP Simplification](../decisions/D013-mcp-simplification.md)
- [Decision: D002 MCP Tool Contracts](../decisions/002-mcp-tool-contracts.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)

---

## 2026-03-03 - UI Removal (CLI and MCP Focus)

**What Changed:**
- Removed `hub-ui/` directory (Next.js UI application with ~50+ files)
- Removed `hub-core/src/hub_core/streamlit_app.py` (Streamlit UI)
- Removed `streamlit>=1.28.0` dependency from `hub-core/pyproject.toml`
- Removed `cm ui` command from CLI (`hub-cli/src/hub_cli/main.py`)
- Removed UI-related functions: `ui_command()`, `check_hub_ui()`, `find_free_port()`, `_get_project_path()`
- Removed UI checks from `cm doctor` command (hub-ui and Node.js/npm checks)
- Removed "Start UI Dashboard" option from interactive `cm init` menu
- Archived context files to `context/evolution/archived/`:
  - `feature-hub-ui.md` (UI feature intent)
  - `006-ui-readonly-by-default.md` (UI design decision)

**Why:**
- Focus exclusively on CLI and MCP as primary interfaces
- Reduce maintenance burden and complexity
- Eliminate Node.js dependency requirement (was barrier to adoption)
- Simplify deployment - single stack (Python only)
- UI was read-only and didn't provide value beyond what CLI/MCP offers
- Streamline distribution and installation process

**Technical Details:**
- `hub-core` now has only one dependency: `fastmcp>=2.0.0,<3.0.0`
- CLI retains all core commands: `config`, `doctor`, `init`, `projects`, `agents`, `setup-commands`
- MCP server remains fully intact with all tools (intent, build, learn, verify)
- Users interact via CLI commands or MCP tools in their AI editor

**Related:**
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)
- [Decision: Distribution and Installation](../decisions/011-distribution-and-installation.md)

---

## 2026-01-31 - Context Mesh Evolution Strategy Implementation

**What Changed:**
- Implemented CLI slash commands following Intent → Build → Learn workflow
  - `/intent` commands: new-project, add-feature, fix-bug, update, create-agent, status
  - `/build` commands: plan, approve, execute, clarify, gate, status
  - `/learn` commands: sync, review, apply, status, retrospective
- Added proactive MCP tools for active intelligence
  - `cm_lifecycle_state` - Current phase with recommendations
  - `cm_clarify` - Pre-build clarifying questions
  - `cm_gate_check` - Quality gate verification
  - `cm_suggest_next` - Next action suggestions
  - `cm_workflow_guide` - Complete workflow status
- Implemented quality gates system for phase transitions
  - Intent → Build gate: Feature complete, ADR exists, no validation errors
  - Build → Learn gate: Implementation complete, tests pass, AC met
- Enhanced Hub UI with new components
  - MCP client library (`lib/mcp-client.ts`)
  - React hooks (`hooks/useContextMesh.ts`)
  - API route (`app/api/mcp/route.ts`)
  - RelationshipGraph component (features ↔ decisions visualization)
  - BuildDashboard component (gate status and workflow)
  - WorkflowStatus component (lifecycle state and suggestions)
- Created Framework v1.2.0 prompt templates
  - `clarify.md` - Pre-build clarification questions
  - `checkpoint.md` - Quality gate verification
  - `retrospective.md` - Post-implementation reflection
- Updated `.context-mesh-framework.md` with Quality Gates section

**Why:**
- Provide multiple interfaces (CLI, MCP, UI) for same functionality
- Make the system proactive rather than purely reactive
- Enforce governance through quality gates without blocking users
- Maintain Context Mesh identity and a clear "Operational System of Context"
- Create a complete "Operational System of Context"

**Technical Details:**
- CLI uses Typer with slash command subgroups
- MCP tools analyze context state and generate recommendations
- UI uses Next.js API routes to communicate with Python MCP server
- Quality gates can be checked manually (prompts) or automatically (MCP tools)

**Related:**
- [Decision: Context Mesh Evolution Strategy](../decisions/012-context-mesh-evolution-strategy.md)
- [Feature: Hub CLI](../intent/feature-hub-cli.md)
- [Feature: Hub Core](../intent/feature-hub-core.md)

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
- `cm` - Interactive menu

**AI Agent Support:**
- **IDE Agents**: Cursor, GitHub Copilot (use MCP in editor)
- **CLI Agents**: Gemini CLI, Claude Code (use agent chat with MCP; slash commands later)

**Why:**
- Stack unification: Python for hub-core and hub-cli
- Better integration with FastMCP
- Simpler dependency management
- Interactive init pattern for AI agent selection
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
- Updated feature intents to reference Decision 010 (hub-core, hub-build-protocol, hub-cli, hub-learn-sync)
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
- [Feature: Hub Learn Sync](../intent/feature-hub-learn-sync.md)
