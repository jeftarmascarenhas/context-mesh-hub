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

_Explain why this project matters_

## Status

- **Created**: {today}
- **Status**: Active
""",
                "context/evolution/changelog.md": f"""# Changelog

## [{today}] - Initialized

### Added
- Context Mesh initialized
- Project intent created
""",
                "context/decisions/.gitkeep": "",
                "context/knowledge/patterns/.gitkeep": "",
                "context/knowledge/anti-patterns/.gitkeep": "",
                "context/agents/.gitkeep": "",
                "AGENTS.md": f"""# AGENTS.md

> Load @context/ files before implementing.

## Project: {name}

## Workflow
Intent → Build → Learn

## Files to Load
- @context/intent/project-intent.md
- @context/decisions/*.md
- @context/intent/F*.md (feature intents)

## Quick Reference
- Features: context/intent/F00X-*.md
- Decisions: context/decisions/D00X-*.md
- Patterns: context/knowledge/patterns/*.md
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
                    "context/intent/project-intent.md": f"# Project Intent: {name}\n\n## What\n\n_Based on analysis: {', '.join(analysis.frameworks) or 'custom project'}_\n\n## Why\n\n_Add project purpose_",
                    "context/decisions/D001-tech-stack.md": f"# Decision D001: Tech Stack\n\n## Context\n\nExisting project with {', '.join(analysis.languages)} codebase.\n\n## Decision\n\nContinue with: {', '.join(analysis.frameworks)}\n\n## Status\n\nAccepted",
                    "AGENTS.md": f"# AGENTS.md\n\n> Load @context/ files.\n\n## Project: {name}\n\nLanguages: {', '.join(analysis.languages)}",
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
