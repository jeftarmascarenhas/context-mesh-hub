"""Intent Service - CRUD for features, decisions, bugs, and project intent.

Pure business logic with dependency injection.
All I/O operations delegated to infrastructure layer.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import date
import re

from ...loader import ContextLoader
from ...infrastructure.parsers.markdown_parser import MarkdownParser
from ...shared.errors import ArtifactNotFoundError, ValidationError


class IntentService:
    """Service for managing Context Mesh intent artifacts.
    
    Handles CRUD operations for:
    - Features (F001-name.md)
    - Decisions (D001-name.md)
    - Bugs (bug-name.md)
    - Project intent (project-intent.md)
    """
    
    def __init__(self, loader: ContextLoader, parser: MarkdownParser):
        """Initialize intent service with dependencies.
        
        Args:
            loader: ContextLoader instance for accessing artifacts
            parser: MarkdownParser for extracting markdown sections
        """
        self.loader = loader
        self.parser = parser
    
    # ========================================================================
    # FEATURE OPERATIONS
    # ========================================================================
    
    def create_feature(
        self,
        title: str,
        what: str,
        why: str,
        acceptance_criteria: Optional[List[str]] = None,
        related_decisions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new feature intent.
        
        Args:
            title: Feature title
            what: What the feature does
            why: Why the feature is needed
            acceptance_criteria: List of acceptance criteria
            related_decisions: List of related decision IDs
        
        Returns:
            Dict with file_path and file_content
        """
        index = self.loader.index
        feat_num = self._get_next_feature_number(index)
        slug = self._slugify(title)
        file_path = f"context/intent/{feat_num}-{slug}.md"
        today = date.today().isoformat()
        
        ac_list = acceptance_criteria or ["Criteria 1", "Criteria 2"]
        ac_items = "\n".join(f"- [ ] {ac}" for ac in ac_list)
        
        related_dec = "\n".join(f"- {d}" for d in (related_decisions or [])) or "_None yet_"
        
        dec_ids = [d.replace("D", "").replace("-", "").strip() if isinstance(d, str) and d.startswith("D") else d for d in (related_decisions or [])]
        dec_ids_yaml = "[" + ", ".join(f'"{d}"' if d else "" for d in dec_ids) + "]" if dec_ids else "[]"
        
        file_content = f"""---
id: {feat_num}
type: feature
title: {title}
status: draft
priority: medium
created: {today}
updated: {today}
depends_on: []
decisions: {dec_ids_yaml}
agents: []
---

# Feature {feat_num}: {title}

## What

{what}

## Why

{why}

## Acceptance Criteria

{ac_items}

## Related Decisions

{related_dec}
"""
        
        return {
            "id": feat_num,
            "file_path": file_path,
            "file_content": file_content,
        }
    
    def get_feature(self, name: str) -> Dict[str, Any]:
        """Get a feature by ID or slug.
        
        Args:
            name: Feature ID (F001) or slug
        
        Returns:
            Dict with name, path, content, status, title
            
        Raises:
            ArtifactNotFoundError: If feature not found
        """
        index = self.loader.index
        artifact = index["feature_intents"].get(name)
        
        # Try finding by slug if not found directly
        if not artifact:
            for k, v in index["feature_intents"].items():
                if name.lower() in k.lower() or name.lower() in v.get("path", "").lower():
                    artifact = v
                    name = k
                    break
        
        if not artifact:
            available = list(index["feature_intents"].keys())[:10]
            raise ArtifactNotFoundError(
                f"Feature not found: {name}",
                artifact_type="feature",
                artifact_name=name,
                details={"available": available}
            )
        
        content = artifact.get("content", "")
        return {
            "name": name,
            "path": artifact["path"],
            "content": content,
            "status": self.parser.extract_status(content),
            "title": self.parser.extract_title(content),
        }
    
    def list_features(self) -> List[Dict[str, Any]]:
        """List all features.
        
        Returns:
            List of dicts with name, path, status, title
        """
        index = self.loader.index
        features = []
        
        for feat_name, artifact in index["feature_intents"].items():
            # Skip bugs
            if "bug" in artifact.get("path", "").lower():
                continue
            
            content = artifact.get("content", "")
            features.append({
                "name": feat_name,
                "path": artifact.get("path", ""),
                "status": self.parser.extract_status(content),
                "title": self.parser.extract_title(content),
            })
        
        return features
    
    def update_feature(self, name: str, updates: Dict[str, str]) -> Dict[str, Any]:
        """Update a feature's sections.
        
        Args:
            name: Feature ID or slug
            updates: Dict of section names to new content
        
        Returns:
            Dict with updated content and file path
            
        Raises:
            ArtifactNotFoundError: If feature not found
        """
        feature = self.get_feature(name)
        existing_content = feature["content"]
        
        updated_content = self._update_sections(existing_content, updates)
        
        return {
            "name": name,
            "path": feature["path"],
            "updated_content": updated_content,
        }
    
    # ========================================================================
    # DECISION OPERATIONS
    # ========================================================================
    
    def create_decision(
        self,
        title: str,
        context: str,
        decision: str,
        rationale: str,
        alternatives: Optional[List[Dict[str, str]]] = None,
        consequences: Optional[Dict[str, List[str]]] = None,
        related_features: Optional[List[str]] = None,
        related_decisions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new decision.
        
        Args:
            title: Decision title
            context: Context and constraints
            decision: The decision made
            rationale: Why this decision was made
            alternatives: List of alternatives with name and reason
            consequences: Dict with 'positive' and 'tradeoffs' lists
            related_features: List of related feature IDs
            related_decisions: List of related decision IDs
        
        Returns:
            Dict with file_path and file_content
        """
        index = self.loader.index
        dec_num = self._get_next_decision_number(index)
        slug = self._slugify(title)
        file_path = f"context/decisions/{dec_num}-{slug}.md"
        today = date.today().isoformat()
        
        # Format alternatives
        alt_list = alternatives or []
        alt_items = "\n".join(
            f"- **{alt.get('name', 'Alt')}**: {alt.get('reason', 'Not chosen')}"
            for alt in alt_list
        ) or "_None documented_"
        
        # Format consequences
        cons = consequences or {"positive": ["_Benefits_"], "tradeoffs": ["_Trade-offs_"]}
        pos_items = "\n".join(f"- {c}" for c in cons.get("positive", ["_Benefits_"]))
        trade_items = "\n".join(f"- {c}" for c in cons.get("tradeoffs", ["_Trade-offs_"]))
        
        # Format related
        rel_feat = ", ".join(related_features or []) or "_None_"
        rel_dec = ", ".join(related_decisions or []) or "_None_"
        
        # Extract IDs for YAML
        feat_ids = [f.replace("F", "").replace("-", "").strip() if isinstance(f, str) and f.startswith("F") else f for f in (related_features or [])]
        feat_ids_yaml = "[" + ", ".join(f'"{f}"' if f else "" for f in feat_ids) + "]" if feat_ids else "[]"
        
        file_content = f"""---
id: {dec_num}
type: decision
title: {title}
status: accepted
created: {today}
updated: {today}
features: {feat_ids_yaml}
supersedes: null
superseded_by: null
related: []
---

# Decision {dec_num}: {title}

## Context

{context}

## Decision

{decision}

## Rationale

{rationale}

## Alternatives Considered

{alt_items}

## Consequences

### Positive
{pos_items}

### Trade-offs
{trade_items}

## Related

- Features: {rel_feat}
- Decisions: {rel_dec}
"""
        
        return {
            "id": dec_num,
            "file_path": file_path,
            "file_content": file_content,
        }
    
    def get_decision(self, name: str) -> Dict[str, Any]:
        """Get a decision by ID or number.
        
        Args:
            name: Decision ID (D001) or number (001)
        
        Returns:
            Dict with name, path, content, status, title
            
        Raises:
            ArtifactNotFoundError: If decision not found
        """
        index = self.loader.index
        
        # Normalize name (D001 or 001)
        norm_name = name if name.startswith("D") else name.lstrip("0") or "1"
        artifact = index["decisions"].get(name) or index["decisions"].get(norm_name)
        
        if not artifact:
            available = list(index["decisions"].keys())[:10]
            raise ArtifactNotFoundError(
                f"Decision not found: {name}",
                artifact_type="decision",
                artifact_name=name,
                details={"available": available}
            )
        
        content = artifact.get("content", "")
        return {
            "name": name,
            "path": artifact["path"],
            "content": content,
            "status": self.parser.extract_status(content),
            "title": self.parser.extract_title(content),
        }
    
    def list_decisions(self) -> List[Dict[str, Any]]:
        """List all decisions.
        
        Returns:
            List of dicts with number, path, title, status
        """
        index = self.loader.index
        decisions = []
        
        for dec_num, artifact in index["decisions"].items():
            content = artifact.get("content", "")
            decisions.append({
                "number": dec_num,
                "path": artifact.get("path", ""),
                "title": self.parser.extract_title(content),
                "status": self.parser.extract_status(content),
            })
        
        # Sort by number
        decisions.sort(key=lambda x: x["number"])
        return decisions
    
    def update_decision(self, name: str, updates: Dict[str, str]) -> Dict[str, Any]:
        """Update a decision's sections.
        
        Args:
            name: Decision ID or number
            updates: Dict of section names to new content
        
        Returns:
            Dict with updated content and file path
            
        Raises:
            ArtifactNotFoundError: If decision not found
        """
        decision = self.get_decision(name)
        existing_content = decision["content"]
        
        updated_content = self._update_sections(existing_content, updates)
        
        return {
            "name": name,
            "path": decision["path"],
            "updated_content": updated_content,
        }
    
    # ========================================================================
    # BUG OPERATIONS
    # ========================================================================
    
    def create_bug(
        self,
        title: str,
        description: str,
        expected: str,
        actual: str,
        impact: Optional[str] = None,
        related_feature: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new bug report.
        
        Args:
            title: Bug title
            description: Bug description
            expected: Expected behavior
            actual: Actual behavior
            impact: Who/what is affected
            related_feature: Related feature ID
        
        Returns:
            Dict with file_path and file_content
        """
        slug = self._slugify(title)
        file_path = f"context/intent/bug-{slug}.md"
        today = date.today().isoformat()
        
        file_content = f"""# Bug: {title}

## Description

{description}

## Expected Behavior

{expected}

## Actual Behavior

{actual}

## Impact

{impact or '_Who/what is affected_'}

## Related Feature

{related_feature or '_Related feature if any_'}

## Status

- **Reported**: {today}
- **Status**: Open
"""
        
        return {
            "file_path": file_path,
            "file_content": file_content,
        }
    
    def get_bug(self, name: str) -> Dict[str, Any]:
        """Get a bug by name or slug.
        
        Args:
            name: Bug slug or partial name
        
        Returns:
            Dict with name, path, content
            
        Raises:
            ArtifactNotFoundError: If bug not found
        """
        index = self.loader.index
        artifact = None
        
        for k, v in index["feature_intents"].items():
            if "bug" in v.get("path", "").lower() and name.lower() in k.lower():
                artifact = v
                name = k
                break
        
        if not artifact:
            raise ArtifactNotFoundError(
                f"Bug not found: {name}",
                artifact_type="bug",
                artifact_name=name
            )
        
        return {
            "name": name,
            "path": artifact["path"],
            "content": artifact["content"],
        }
    
    def list_bugs(self) -> List[Dict[str, Any]]:
        """List all bugs.
        
        Returns:
            List of dicts with name, path, status
        """
        index = self.loader.index
        bugs = []
        
        for bug_name, artifact in index["feature_intents"].items():
            if "bug" in artifact.get("path", "").lower():
                bugs.append({
                    "name": bug_name,
                    "path": artifact.get("path", ""),
                    "status": self.parser.extract_status(artifact.get("content", "")),
                })
        
        return bugs
    
    # ========================================================================
    # PROJECT INTENT OPERATIONS
    # ========================================================================
    
    def get_project_intent(self) -> Dict[str, Any]:
        """Get project intent.
        
        Returns:
            Dict with path and content
            
        Raises:
            ArtifactNotFoundError: If project intent not found
        """
        artifact = self.loader.index.get("project_intent")
        if not artifact:
            raise ArtifactNotFoundError(
                "Project intent not found",
                artifact_type="project",
                artifact_name="project-intent"
            )
        
        return {
            "path": artifact["path"],
            "content": artifact["content"],
        }
    
    # ========================================================================
    # AGENT OPERATIONS
    # ========================================================================
    
    def get_agent(self, name: str) -> Dict[str, Any]:
        """Get an agent by name.
        
        Args:
            name: Agent name (with or without 'agent-' prefix)
        
        Returns:
            Dict with name, path, content
            
        Raises:
            ArtifactNotFoundError: If agent not found
        """
        index = self.loader.index
        
        # Normalize name (allow with/without agent- prefix)
        if not name.startswith("agent-"):
            name = f"agent-{name}"
        
        artifact = index["agents"].get(name)
        if not artifact:
            available = list(index["agents"].keys())[:10]
            raise ArtifactNotFoundError(
                f"Agent not found: {name}",
                artifact_type="agent",
                artifact_name=name,
                details={"available": available}
            )
        
        return {
            "name": name,
            "path": artifact["path"],
            "content": artifact["content"],
        }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents.
        
        Returns:
            List of dicts with name, path
        """
        index = self.loader.index
        agents = []
        
        for agent_name, artifact in index["agents"].items():
            agents.append({
                "name": agent_name,
                "path": artifact.get("path", ""),
            })
        
        return agents
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_next_feature_number(self, index: dict) -> str:
        """Get the next feature number (F001, F002, etc.).
        
        Args:
            index: Context index
        
        Returns:
            Next feature number (e.g., "F002")
        """
        existing = [
            k for k in index["feature_intents"].keys()
            if k.startswith("F") and len(k) >= 4 and k[1:4].isdigit()
        ]
        if existing:
            max_num = max(int(k[1:4]) for k in existing)
            return f"F{max_num + 1:03d}"
        return "F001"
    
    def _get_next_decision_number(self, index: dict) -> str:
        """Get the next decision number (D001, D002, etc.).
        
        Args:
            index: Context index
        
        Returns:
            Next decision number (e.g., "D002")
        """
        existing = list(index["decisions"].keys())
        if existing:
            nums = []
            for d in existing:
                if d.startswith("D") and len(d) >= 4 and d[1:4].isdigit():
                    nums.append(int(d[1:4]))
                elif d.isdigit():
                    nums.append(int(d))
            if nums:
                return f"D{max(nums) + 1:03d}"
        return "D001"
    
    def _slugify(self, text: str) -> str:
        """Convert text to slug.
        
        Args:
            text: Text to slugify
        
        Returns:
            Slug (lowercase, hyphens)
        """
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    
    def _update_sections(self, content: str, updates: Dict[str, str]) -> str:
        """Update specific sections in markdown content.
        
        Args:
            content: Original markdown content
            updates: Dict of section names to new content
        
        Returns:
            Updated content
        """
        updated_content = content
        
        for section, new_value in updates.items():
            section_header = f"## {section.replace('_', ' ').title()}"
            if section_header in updated_content:
                parts = updated_content.split(section_header)
                if len(parts) > 1:
                    rest = parts[1]
                    next_section = rest.find("\n## ")
                    if next_section != -1:
                        updated_content = (
                            parts[0] + section_header + "\n\n" + 
                            str(new_value) + rest[next_section:]
                        )
                    else:
                        updated_content = parts[0] + section_header + "\n\n" + str(new_value)
        
        return updated_content
