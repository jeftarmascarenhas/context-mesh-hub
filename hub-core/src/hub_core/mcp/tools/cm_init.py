"""MCP Tool: cm_init - Project initialization.

Tool 1 of 8: Initialize or migrate Context Mesh projects.

IMPORTANT: This tool is INTERACTIVE. It requires user input before creating files.
The agent MUST ask the user questions and wait for answers before proceeding.
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
    """Register cm_init tool with MCP server."""
    
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
        user_input: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Initialize or migrate a Context Mesh project.
        
        ⚠️ INTERACTIVE WORKFLOW - Agent must ask user questions first!
        
        CORRECT WORKFLOW:
        1. Call cm_init(action="analyze") to get questions
        2. STOP and ask user each question
        3. Wait for user answers
        4. Call cm_init(action="new", user_input={answers})
        
        Actions:
        - "analyze": Get questions to ask the user (START HERE)
        - "new": Create structure (requires user_input with answers)
        - "existing": Add to existing codebase (brownfield)
        - "migrate": Convert old naming conventions
        
        Args:
            action: "analyze", "new", "existing", or "migrate"
            user_input: User's answers (required for "new")
            repo_root: Path to repository root
        
        Examples:
            # Step 1: Get questions
            cm_init(action="analyze")
            
            # Step 2: After asking user
            cm_init(action="new", user_input={
                "project_name": "my-api",
                "description": "REST API for users",
                "business_goal": "Enable user management"
            })
        """
        valid_actions = ["analyze", "new", "existing", "migrate"]
        if action not in valid_actions:
            return {
                "error": f"Invalid action: {action}",
                "valid_actions": valid_actions,
                "tip": "Start with action='analyze' to get questions for the user",
            }
        
        # Get repo path
        if repo_root:
            repo_path = Path(repo_root).resolve()
            active_loader = ContextLoader(repo_path)
            active_loader.load()
        else:
            active_loader = default_loader
            repo_path = active_loader.repo_root
        
        today = date.today().isoformat()
        
        # ====================================================================
        # ACTION: ANALYZE - Return questions for the user
        # ====================================================================
        if action == "analyze":
            return {
                "status": "questions_required",
                "message": "Before creating Context Mesh, I need to understand your project.",
                "agent_instruction": "⚠️ STOP. Ask the user EACH question below. Do NOT proceed until you have answers.",
                "questions": [
                    {
                        "id": "project_name",
                        "question": "What is the name of your project?",
                        "required": True,
                        "example": "user-auth-api, todo-app, ecommerce-platform"
                    },
                    {
                        "id": "description",
                        "question": "Describe what this project does (2-3 sentences).",
                        "required": True,
                        "example": "A REST API that handles user authentication and authorization for mobile apps."
                    },
                    {
                        "id": "business_goal",
                        "question": "What is the main goal of this project? Why does it exist?",
                        "required": True,
                        "example": "Enable secure user login across all company mobile applications."
                    },
                    {
                        "id": "tech_stack",
                        "question": "What technologies will you use? (optional)",
                        "required": False,
                        "example": "Python, FastAPI, PostgreSQL, Redis"
                    },
                    {
                        "id": "constraints",
                        "question": "Any constraints or limitations? (optional)",
                        "required": False,
                        "example": "Must support 10k concurrent users, budget limited"
                    },
                ],
                "next_step": "After getting answers, call: cm_init(action='new', user_input={...})",
            }
        
        # ====================================================================
        # ACTION: NEW - Create new Context Mesh (requires user_input)
        # ====================================================================
        if action == "new":
            # Validate user_input
            if not user_input:
                return {
                    "error": "Missing user_input parameter",
                    "status": "input_required",
                    "agent_instruction": "⚠️ STOP. You must first ask the user questions. Call cm_init(action='analyze') to get the questions.",
                    "workflow": [
                        "1. cm_init(action='analyze') - get questions",
                        "2. Ask user each question",
                        "3. cm_init(action='new', user_input={answers})"
                    ],
                }
            
            # Check required fields
            required = ["project_name", "description", "business_goal"]
            missing = [f for f in required if not user_input.get(f)]
            if missing:
                return {
                    "error": f"Missing required answers: {missing}",
                    "status": "incomplete_input",
                    "agent_instruction": f"⚠️ STOP. Ask the user for: {', '.join(missing)}",
                    "required_fields": required,
                    "provided_fields": list(user_input.keys()),
                }
            
            # Extract values from user input
            name = user_input["project_name"]
            desc = user_input["description"]
            goal = user_input["business_goal"]
            tech = user_input.get("tech_stack", "")
            constraints = user_input.get("constraints", "")
            
            # Build tech stack section
            tech_section = f"\n### Technology Stack\n{tech}" if tech else ""
            constraints_section = f"\n## Constraints\n\n{constraints}" if constraints else "\n## Constraints\n\n_None specified_"
            
            # Generate files with REAL user content
            files_to_create = {
                "context/intent/project-intent.md": f"""---
type: project
title: {name}
status: active
created: {today}
updated: {today}
---

# Project Intent: {name}

## What

{desc}

## Why

{goal}

### Business Value

{goal}
{tech_section}

## Scope

### Core Capabilities

_Define after creating first features_

### Out of Scope (v1)

_Define what is explicitly NOT included_

## Acceptance Criteria

### Functional

- [ ] _Add criteria after defining features_

### Non-Functional

- [ ] _Add non-functional requirements_
{constraints_section}

## Related

- Features will be linked here as they are created
""",
                "context/evolution/changelog.md": f"""# Changelog

This file tracks the evolution of the project.

---

## {today} - Project Initialized

**What Changed:**
- Context Mesh structure created
- Project intent defined: {name}

**Why:**
{goal}

**Next Steps:**
- Create first feature with cm_intent(action='create', type='feature')
- Document technical decisions as they are made
""",
                "context/decisions/.gitkeep": "",
                "context/knowledge/patterns/.gitkeep": "",
                "context/knowledge/anti-patterns/.gitkeep": "",
                "context/agents/.gitkeep": "",
                "AGENTS.md": _generate_agents_md(name),
            }
            
            return {
                "status": "ready_to_create",
                "message": f"Ready to create Context Mesh for '{name}'",
                "agent_instruction": "Show the user what will be created and ask for confirmation before creating files.",
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
                    "1. Review the files above with the user",
                    "2. Create the files after user approval",
                    "3. Use cm_intent to add features",
                ],
            }
        
        # ====================================================================
        # ACTION: EXISTING - Analyze existing codebase for brownfield
        # ====================================================================
        elif action == "existing":
            scanner = RepositoryScanner(repo_path)
            slice_gen = SliceGenerator(scanner)
            extractor = ContextExtractor(scanner)
            
            analysis = scanner.scan()
            slices = slice_gen.generate_slices("directory", analysis)
            
            proposed_artifacts = []
            for slice_def in slices[:5]:
                artifacts = extractor.extract_from_slice(slice_def, analysis)
                proposed_artifacts.extend(artifacts)
            
            return {
                "status": "analysis_complete",
                "action": "existing",
                "repo_path": str(repo_path),
                "analysis": {
                    "total_files": analysis.get("total_files", 0),
                    "languages": analysis.get("languages", {}),
                    "directories": analysis.get("directories", [])[:10],
                },
                "slices_generated": len(slices),
                "proposed_artifacts": proposed_artifacts[:10],
                "agent_instruction": "Show this analysis to the user and ask what they want to extract.",
                "next_steps": [
                    "1. Review the analysis with the user",
                    "2. Ask which areas to focus on",
                    "3. Use cm_analyze(action='extract') for detailed extraction",
                ],
            }
        
        # ====================================================================
        # ACTION: MIGRATE - Convert old naming to new
        # ====================================================================
        elif action == "migrate":
            index = active_loader.index
            migrations = []
            
            intent_dir = active_loader.context_dir / "intent"
            if intent_dir.exists():
                for f in intent_dir.glob("feature-*.md"):
                    old_name = f.name
                    slug = old_name.replace("feature-", "").replace(".md", "")
                    new_number = _get_next_feature_number(index)
                    new_name = f"{new_number}-{slug}.md"
                    migrations.append({
                        "type": "feature",
                        "old_path": str(f.relative_to(active_loader.repo_root)),
                        "new_path": f"context/intent/{new_name}",
                    })
                    index["feature_intents"][new_number] = {"path": str(f)}
            
            decisions_dir = active_loader.context_dir / "decisions"
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
                                "old_path": str(f.relative_to(active_loader.repo_root)),
                                "new_path": f"context/decisions/{new_name}",
                            })
            
            if not migrations:
                return {
                    "action": "migrate",
                    "status": "no_changes",
                    "message": "No files need migration. Already using new naming convention.",
                }
            
            return {
                "action": "migrate",
                "status": "migrations_found",
                "migrations": migrations,
                "migration_count": len(migrations),
                "agent_instruction": "Show these migrations to the user and ask for confirmation.",
                "commands": [f"git mv '{m['old_path']}' '{m['new_path']}'" for m in migrations],
            }
    
    return cm_init


def _get_next_feature_number(index: dict) -> str:
    """Get the next feature number (F001, F002, etc.)."""
    existing = [
        k for k in index.get("feature_intents", {}).keys()
        if k.startswith("F") and len(k) >= 4 and k[1:4].isdigit()
    ]
    if existing:
        max_num = max(int(k[1:4]) for k in existing)
        return f"F{max_num + 1:03d}"
    return "F001"


def _generate_agents_md(project_name: str) -> str:
    """Generate AGENTS.md content."""
    return f'''# AGENTS.md - {project_name}

> **For AI Agents**: This project follows the **Context Mesh** framework.
> Before writing any code, you MUST load and understand the context files.

---

## 🧠 Context Mesh Framework

**Workflow**: Intent → Build → Learn

1. **Intent**: Understand WHAT and WHY before coding
2. **Build**: Implement following decisions and patterns
3. **Learn**: Capture learnings back into context

---

## 📂 Context Structure

```
context/
├── intent/           # WHAT to build and WHY
│   ├── project-intent.md      # Project vision
│   └── F00X-*.md              # Feature requirements
├── decisions/        # HOW to build
│   └── D00X-*.md              # Technical decisions
├── knowledge/        # Patterns and anti-patterns
│   ├── patterns/
│   └── anti-patterns/
├── agents/           # Execution agents
└── evolution/        # Project history
    └── changelog.md
```

---

## 🤖 AI Agent Instructions

### Before Any Implementation

1. Load `@context/intent/project-intent.md`
2. Load relevant `@context/intent/F00X-*.md`
3. Load `@context/decisions/*.md`

### During Implementation

1. Follow patterns from `@context/knowledge/patterns/`
2. Avoid anti-patterns
3. Respect documented decisions
4. Stay within scope

### After Implementation

1. Update feature status
2. Update changelog.md

---

## ⚠️ Rules

### ✅ ALWAYS
- Load context before implementing
- Follow documented decisions
- Update context after implementation
- Ask user for clarification when needed

### ❌ NEVER
- Ignore documented decisions
- Create files without user approval
- Assume content - always ask
- Skip loading intent files

---

## 📖 References

- [Context Mesh Framework](https://github.com/jeftarmascarenhas/context-mesh)
'''
