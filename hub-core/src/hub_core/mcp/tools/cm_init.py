"""MCP Tool: cm_init - Project initialization.

Tool 1 of 8: Initialize or migrate Context Mesh projects.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import date
import re

from fastmcp import FastMCP

from ...loader import ContextLoader
from ...validator import ContextValidator
from ...infrastructure.parsers.markdown_parser import MarkdownParser
from ...infrastructure.scanner.repo_scanner import RepositoryScanner
from ...infrastructure.scanner.slice_generator import SliceGenerator
from ...infrastructure.scanner.context_extractor import ContextExtractor
from ..decorators import handle_mcp_errors


def register_cm_init(
    mcp: FastMCP,
    loader: ContextLoader,
    validator: ContextValidator,
    parser: MarkdownParser,
):
    """Register cm_init tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        loader: Default ContextLoader
        validator: ContextValidator instance
        parser: MarkdownParser instance
    """
    
    # Keep reference to default loader for fallback
    default_loader = loader
    
    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    @handle_mcp_errors
    def cm_init(
        action: str,
        project_name: Optional[str] = None,
        project_description: Optional[str] = None,
        repo_root: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initialize or migrate a Context Mesh project.
        
        Consolidates project setup into a single tool with three actions:
        - "new": Create new Context Mesh structure with full setup
        - "existing": Add Context Mesh to existing codebase (brownfield)
        - "migrate": Convert old naming conventions to new (feature-*.md → F00X-*.md)
        
        Args:
            action: Action to perform - "new", "existing", or "migrate"
            project_name: Name for the project (optional for "existing" and "migrate")
            project_description: Short description of the project (optional)
            repo_root: Path to repository root. If not provided, uses server default.
        
        Returns:
            Dictionary with:
            - For "new": files_to_create dict with file paths and content
            - For "existing": analysis results and proposed structure
            - For "migrate": list of files to rename and proposed changes
        
        Examples:
            # Create new project
            cm_init(action="new", project_name="my-api", project_description="REST API")
            
            # Add to existing project
            cm_init(action="existing", repo_root="/path/to/project")
            
            # Migrate old naming to new
            cm_init(action="migrate", repo_root="/path/to/project")
        """
        valid_actions = ["new", "existing", "migrate"]
        if action not in valid_actions:
            return {
                "error": f"Invalid action: {action}",
                "valid_actions": valid_actions,
                "tip": "Use 'new' for greenfield, 'existing' for brownfield, 'migrate' to update naming",
            }
        
        # Get components for repo
        if repo_root:
            repo_path = Path(repo_root).resolve()
            loader = ContextLoader(repo_path)
            loader.load()
        else:
            loader = default_loader
            repo_path = loader.repo_root
        
        # Create scanner components on demand (only for "existing" action)
        scanner = RepositoryScanner(repo_path)
        slice_gen = SliceGenerator(scanner)
        extractor = ContextExtractor(scanner)
        
        today = date.today().isoformat()
        
        # ====================================================================
        # ACTION: NEW - Create new Context Mesh structure
        # ====================================================================
        if action == "new":
            name = project_name or loader.repo_root.name
            desc = project_description or "_Describe what this project does_"
            
            files_to_create = {
                "context/intent/project-intent.md": f"""# Project Intent: {name}

## What

{desc}

## Why

_Why does this project exist? What problem does it solve?_

### Business Value
_Business justification_

### Technical Value
_Technical justification_

## Scope

### Core Capabilities
- Capability 1
- Capability 2

### Out of Scope (v1)
- Out of scope 1
- Out of scope 2

## Acceptance Criteria

### Functional
- [ ] Criterion 1
- [ ] Criterion 2

### Non-Functional
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints

_Technical, business, or organizational constraints_

## Related

- [Feature: F001 - Name](./F001-*.md)
- [Decision: D001 - Name](../decisions/D001-*.md)

## Status

- **Created**: {today}
- **Status**: Active
""",
                "context/evolution/changelog.md": f"""# Changelog

This file tracks the evolution of the project, documenting what changed and why.

---

## {today} - Initialized

**What Changed:**
- Context Mesh structure initialized
- Project intent created
- Directory structure established

**Why:**
Establish Context Mesh framework for AI-First development with clear intent, decisions, and knowledge management.

**Related:**
- Project Intent: [context/intent/project-intent.md](../intent/project-intent.md)

**Next Steps:**
- Define first feature intents
- Document technical decisions
- Add patterns and anti-patterns as they emerge
""",
                "context/decisions/.gitkeep": "",
                "context/knowledge/patterns/.gitkeep": "",
                "context/knowledge/anti-patterns/.gitkeep": "",
                "context/agents/.gitkeep": "",
                "AGENTS.md": f"""# AGENTS.md - {name}

> **For AI Agents**: This project follows the **Context Mesh** framework.
> Before writing any code, you MUST load and understand the context files.

---

## 📖 Artifact Specifications

**CRITICAL**: Before creating or updating any Context Mesh artifact, load the specifications:

📋 **Load**: `@context/knowledge/ARTIFACT_SPECS.md`

This file defines:
- ✅ Required sections for each artifact type (Feature, Decision, Pattern, etc.)
- ⚠️ Recommended sections
- ❌ Optional sections
- 📝 Naming conventions (`F00X-*.md`, `D00X-*.md`)
- 🔗 Cross-reference rules
- ✅ Validation rules

**Never create artifacts from scratch without consulting ARTIFACT_SPECS.md first.**

---

## 🧠 Context Mesh Framework

This project uses [Context Mesh](https://github.com/jeftarmascarenhas/context-mesh) for AI-First development.

**Workflow**: Intent → Build → Learn

1. **Intent** (Step 1): Understand WHAT and WHY before coding
2. **Build** (Step 2): Implement following decisions, patterns, and governance boundaries
3. **Learn** (Step 3): Propose and sync learnings into context artifacts (never automatic)

---

## 📂 Context Structure

```
context/
├── intent/           # WHAT to build and WHY (load first)
│   ├── project-intent.md      # Project vision and goals
│   └── F00X-*.md              # Feature requirements + Acceptance Criteria
├── decisions/        # HOW to build (technical + governance)
│   └── D00X-*.md              # Decisions with rationale
├── knowledge/        # Patterns and anti-patterns
│   ├── patterns/              # Code patterns to FOLLOW
│   └── anti-patterns/         # What to AVOID
├── agents/           # Execution agents for each phase
│   └── agent-*.md             # Step-by-step instructions + Definition of Done
└── evolution/        # Project history
    └── changelog.md           # What changed and why
```

---

## 🚀 Quick Start

```bash
# Add your build/run commands here
```

## 🤖 AI Agent Instructions

### Before Any Implementation

1. **Load project intent**: `@context/intent/project-intent.md`
2. **Load feature intent**: `@context/intent/F00X-*.md` (for the feature you're implementing)
3. **Load decisions**: `@context/decisions/*.md` (relevant to the feature)
4. **Load patterns**: `@context/knowledge/patterns/*.md`
5. **Load anti-patterns**: `@context/knowledge/anti-patterns/*.md`

### During Implementation

1. **Follow patterns**: Use patterns from `@context/knowledge/patterns/`
2. **Avoid anti-patterns**: Check `@context/knowledge/anti-patterns/`
3. **Respect decisions**: All technical choices are documented in `@context/decisions/`
4. **Stay within scope**: Do not expand feature scope without updating context and user approval

### After Implementation

1. **Mark feature as completed** in the intent file
2. **Add outcomes** to decision files (what worked, what didn't)
3. **Update changelog.md** with what changed

## 📚 Context Files to Load

**Always load (before any work):**
- `@context/intent/project-intent.md` - Project vision and constraints

**Load per feature:**
- `@context/intent/F00X-*.md` - Feature requirements (has Acceptance Criteria)

**Load per phase:**
- `@context/decisions/*.md` - Technical decisions
- `@context/knowledge/patterns/*.md` - Patterns to follow
- `@context/knowledge/anti-patterns/*.md` - What to avoid

## ✅ Definition of Done

General checklist:
- [ ] All Acceptance Criteria in the feature intent are met
- [ ] Code follows patterns from `@context/knowledge/patterns/`
- [ ] No anti-patterns introduced
- [ ] Build passes without errors
- [ ] Tests pass (if applicable)
- [ ] Context updated (Intent / Decisions / Changelog)

## ⚠️ AI Agent Rules

### ✅ ALWAYS
- Load context files before implementing
- Follow decisions from `@context/decisions/`
- Use patterns from `@context/knowledge/patterns/`
- Update context after implementation
- Check Definition of Done before completing

### ❌ NEVER
- Ignore documented decisions
- Use patterns from `@context/knowledge/anti-patterns/`
- Leave context stale after implementation
- Skip loading intent files
- Implement without understanding the WHY

### 📝 File Creation Rules (CRITICAL)

**When to CREATE files:**
- ✅ User explicitly asks to create/implement/add something
- ✅ User uses prompts like "add feature", "fix bug", "implement"
- ✅ User explicitly requests: "create", "make", "build", "generate"

**When to NOT create files (Questions/Explanations):**
- ❌ User asks a question (e.g., "How does X work?", "What is Y?")
- ❌ User asks for explanation or clarification
- ❌ User is exploring or learning about the codebase

## 🔄 Context Update (Critical)

After completing any feature:

1. Update `@context/intent/F00X-*.md`
   - Mark as completed
   - Add any learnings

2. Update `@context/decisions/*.md`
   - Add outcomes section
   - Document what worked/didn't

3. Update `@context/evolution/changelog.md`
   - What changed
   - Why it changed

**Never leave context stale. Future AI sessions depend on accurate context.**

---

## 📖 References

- [Context Mesh Framework](https://github.com/jeftarmascarenhas/context-mesh)
- [AGENTS.md Standard](https://agents.md/)
""",
            }
            
            return {
                "action": "new",
                "project_name": name,
                "files_to_create": files_to_create,
                "file_count": len(files_to_create),
                "structure": [
                    "context/",
                    "├── intent/",
                    "│   └── project-intent.md",
                    "├── decisions/",
                    "├── knowledge/",
                    "│   ├── patterns/",
                    "│   └── anti-patterns/",
                    "├── agents/",
                    "└── evolution/",
                    "    └── changelog.md",
                    "AGENTS.md",
                ],
                "next_steps": [
                    "1. Create these files in your project",
                    "2. Edit project-intent.md with your details",
                    "3. Use cm_intent(action='create', type='feature') to add features",
                ],
            }
        
        # ====================================================================
        # ACTION: EXISTING - Analyze existing codebase for brownfield setup
        # ====================================================================
        elif action == "existing":
            # Scan repository
            analysis = scanner.scan()
            
            # Generate slices
            slices = slice_gen.generate_slices("directory", analysis)
            
            # Extract proposed artifacts (limit to top 5 slices)
            proposed_artifacts = []
            for slice_def in slices[:5]:
                artifacts = extractor.extract_from_slice(slice_def, analysis)
                proposed_artifacts.extend(artifacts)
            
            name = project_name or loader.repo_root.name
            
            return {
                "action": "existing",
                "project_name": name,
                "analysis": {
                    "languages": sorted(list(analysis.languages)),
                    "frameworks": sorted(list(analysis.frameworks)),
                    "entry_points": analysis.entry_points,
                    "build_tools": analysis.build_tools,
                    "file_count": analysis.file_count,
                },
                "slices_found": len(slices),
                "proposed_artifacts": [
                    {
                        "type": a.artifact_type,
                        "title": a.title,
                        "confidence": a.confidence.value,
                    }
                    for a in proposed_artifacts[:10]
                ],
                "files_to_create": {
                    "context/intent/project-intent.md": f"""# Project Intent: {name}

## What

Existing {', '.join(analysis.languages)} project.

_Based on analysis: {', '.join(analysis.frameworks) or 'custom project'}_

## Why

_Add project purpose and business value_

### Business Value
_Business justification_

### Technical Value
_Technical justification_

## Scope

### Core Capabilities
- Capability 1 (based on existing codebase)
- Capability 2

### Out of Scope (v1)
- Out of scope 1

## Acceptance Criteria

### Functional
- [ ] Criterion 1
- [ ] Criterion 2

### Non-Functional
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints

- Existing codebase: {analysis.file_count} files
- Languages: {', '.join(analysis.languages)}
- Build tools: {', '.join(analysis.build_tools)}

## Related

- [Decision: D001 - Tech Stack](../decisions/D001-tech-stack.md)

## Status

- **Created**: {today}
- **Status**: Active
""",
                    "context/decisions/D001-tech-stack.md": f"""# Decision: Tech Stack

## Context

Existing project with {', '.join(analysis.languages)} codebase.

Detected frameworks: {', '.join(analysis.frameworks) or 'None detected'}
Build tools: {', '.join(analysis.build_tools)}
Entry points: {', '.join(analysis.entry_points) if analysis.entry_points else 'To be identified'}

## Decision

Continue with existing tech stack:
- Languages: {', '.join(analysis.languages)}
- Frameworks: {', '.join(analysis.frameworks) or 'Custom/None'}
- Build tools: {', '.join(analysis.build_tools)}

## Rationale

Brownfield project - maintaining existing technology choices for continuity and to leverage existing codebase.

## Alternatives Considered

- Full rewrite: Rejected due to cost and risk
- Incremental migration: Consider for future iterations

## Consequences

### Positive
- Leverage existing codebase and knowledge
- Lower risk of disruption
- Faster time to value

### Trade-offs
- Inherit technical debt from existing codebase
- May need to address legacy patterns over time

## Related

- [Project Intent](../intent/project-intent.md)

## Status

- **Created**: {today}
- **Status**: Accepted
""",
                    "AGENTS.md": f"""# AGENTS.md - {name}

> **For AI Agents**: This project follows the **Context Mesh** framework.
> Before writing any code, you MUST load and understand the context files.

---

## 📖 Artifact Specifications

**CRITICAL**: Before creating or updating any Context Mesh artifact, load the specifications:

📋 **Load**: `@context/knowledge/ARTIFACT_SPECS.md`

**Never create artifacts from scratch without consulting ARTIFACT_SPECS.md first.**

---

## 🧠 Context Mesh Framework

This project uses [Context Mesh](https://github.com/jeftarmascarenhas/context-mesh) for AI-First development.

**Workflow**: Intent → Build → Learn

---

## 📂 Existing Codebase

- **Languages**: {', '.join(analysis.languages)}
- **Frameworks**: {', '.join(analysis.frameworks) or 'Custom/None'}
- **File Count**: {analysis.file_count}
- **Build Tools**: {', '.join(analysis.build_tools)}

## 📂 Context Structure

```
context/
├── intent/           # WHAT to build and WHY
│   ├── project-intent.md
│   └── F00X-*.md
├── decisions/        # HOW to build
│   └── D00X-*.md
├── knowledge/        # Patterns and anti-patterns
│   ├── patterns/
│   └── anti-patterns/
└── evolution/
    └── changelog.md
```

## 🤖 AI Agent Instructions

### Before Any Implementation

1. **Load project intent**: `@context/intent/project-intent.md`
2. **Load feature intent**: `@context/intent/F00X-*.md`
3. **Load decisions**: `@context/decisions/*.md`
4. **Load patterns**: `@context/knowledge/patterns/*.md`

### During Implementation

1. **Follow patterns**: Use patterns from `@context/knowledge/patterns/`
2. **Avoid anti-patterns**: Check `@context/knowledge/anti-patterns/`
3. **Respect decisions**: All technical choices in `@context/decisions/`
4. **Stay within scope**: Do not expand without approval

### After Implementation

1. Update feature intent file
2. Add outcomes to decision files
3. Update changelog.md

## ⚠️ AI Agent Rules

### ✅ ALWAYS
- Load context files before implementing
- Follow decisions from `@context/decisions/`
- Use patterns from `@context/knowledge/patterns/`
- Update context after implementation

### ❌ NEVER
- Ignore documented decisions
- Leave context stale after implementation
- Skip loading intent files

---

## 📖 References

- [Context Mesh Framework](https://github.com/jeftarmascarenhas/context-mesh)
""",
                },
                "next_steps": [
                    "1. Review the analysis above",
                    "2. Create the suggested files",
                    "3. Use cm_analyze(action='extract') for detailed artifact extraction",
                ],
            }
        
        # ====================================================================
        # ACTION: MIGRATE - Convert old naming to new naming convention
        # ====================================================================
        elif action == "migrate":
            index = loader.index
            migrations = []
            
            # Check for old-style feature files (feature-*.md)
            intent_dir = loader.context_dir / "intent"
            if intent_dir.exists():
                for f in intent_dir.glob("feature-*.md"):
                    old_name = f.name
                    slug = old_name.replace("feature-", "").replace(".md", "")
                    new_number = _get_next_feature_number(index)
                    new_name = f"{new_number}-{slug}.md"
                    migrations.append({
                        "type": "feature",
                        "old_path": str(f.relative_to(loader.repo_root)),
                        "new_path": f"context/intent/{new_name}",
                        "old_name": old_name,
                        "new_name": new_name,
                    })
                    # Update index to track numbering
                    index["feature_intents"][new_number] = {"path": str(f)}
            
            # Check for old-style decision files (001-*.md without D prefix)
            decisions_dir = loader.context_dir / "decisions"
            if decisions_dir.exists():
                for f in decisions_dir.glob("[0-9][0-9][0-9]-*.md"):
                    old_name = f.name
                    if not old_name.startswith("D"):
                        match = re.match(r"(\d{3})-(.+)\.md", old_name)
                        if match:
                            num, slug = match.groups()
                            new_name = f"D{num}-{slug}.md"
                            migrations.append({
                                "type": "decision",
                                "old_path": str(f.relative_to(loader.repo_root)),
                                "new_path": f"context/decisions/{new_name}",
                                "old_name": old_name,
                                "new_name": new_name,
                            })
            
            if not migrations:
                return {
                    "action": "migrate",
                    "migrations": [],
                    "message": "No files need migration. Already using new naming convention.",
                }
            
            return {
                "action": "migrate",
                "migrations": migrations,
                "migration_count": len(migrations),
                "instructions": [
                    "Review the proposed migrations above",
                    "Use 'git mv old_path new_path' to rename each file",
                    "Update any references in other files",
                ],
                "tip": "Run 'git mv' commands to preserve Git history",
            }


def _get_next_feature_number(index: dict) -> str:
    """Get the next feature number (F001, F002, etc.)."""
    existing = [
        k for k in index["feature_intents"].keys()
        if k.startswith("F") and len(k) >= 4 and k[1:4].isdigit()
    ]
    if existing:
        max_num = max(int(k[1:4]) for k in existing)
        return f"F{max_num + 1:03d}"
    return "F001"
