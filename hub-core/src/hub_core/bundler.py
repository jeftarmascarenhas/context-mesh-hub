"""Bundling engine for deterministic, scoped context bundles."""

import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

from .loader import ContextLoader


@dataclass
class BundleMetadata:
    """Metadata about a context bundle."""
    bundle_id: str
    bundle_type: str  # "project", "feature", "decision"
    identifier: str  # feature name, decision number, or "project"
    timestamp: str
    composition: List[str] = field(default_factory=list)  # List of artifact paths included


class ContextBundler:
    """Generates deterministic, scoped context bundles."""
    
    # Foundational decisions (always included in project bundles)
    FOUNDATIONAL_DECISIONS = {"001"}  # 001-tech-stack
    
    def __init__(self, loader: ContextLoader):
        """Initialize bundler with a context loader.
        
        Args:
            loader: ContextLoader instance with loaded index.
        """
        self.loader = loader
        self.index = loader.index
    
    def bundle_project(self) -> Dict:
        """Generate bundle for project intent.
        
        Per Decision 003:
        - Include: project-intent.md
        - Include: foundational decisions (001-tech-stack)
        - Include: decisions linked by project intent
        - No auto-expansion
        
        Returns:
            Dictionary with bundle content and metadata.
        """
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        composition = []
        artifacts = []
        
        # Always include project intent
        project_intent = self.index.get("project_intent")
        if not project_intent:
            raise ValueError("Project intent not found")
        
        artifacts.append({
            "type": "project_intent",
            "path": project_intent["path"],
            "content": project_intent["content"],
        })
        composition.append(project_intent["path"])
        
        # Include foundational decisions
        for decision_num in self.FOUNDATIONAL_DECISIONS:
            decision = self.index["decisions"].get(decision_num)
            if decision:
                artifacts.append({
                    "type": "decision",
                    "path": decision["path"],
                    "content": decision["content"],
                    "number": decision_num,
                })
                composition.append(decision["path"])
        
        # Include decisions explicitly linked by project intent
        linked_decisions = self._extract_decision_links(project_intent["content"])
        for decision_num in linked_decisions:
            if decision_num not in self.FOUNDATIONAL_DECISIONS:
                decision = self.index["decisions"].get(decision_num)
                if decision:
                    artifacts.append({
                        "type": "decision",
                        "path": decision["path"],
                        "content": decision["content"],
                        "number": decision_num,
                    })
                    composition.append(decision["path"])
        
        metadata = BundleMetadata(
            bundle_id=bundle_id,
            bundle_type="project",
            identifier="project",
            timestamp=timestamp,
            composition=sorted(composition),
        )
        
        return {
            "metadata": {
                "bundle_id": metadata.bundle_id,
                "bundle_type": metadata.bundle_type,
                "identifier": metadata.identifier,
                "timestamp": metadata.timestamp,
                "composition": metadata.composition,
            },
            "artifacts": artifacts,
        }
    
    def bundle_feature(self, feature_name: str) -> Dict:
        """Generate bundle for a feature intent.
        
        Per Decision 003:
        - Include: feature intent
        - Include: project intent (always)
        - Include: decisions linked by feature
        - Include: decisions linked by project intent
        - No feature cross-references unless explicit
        
        Args:
            feature_name: Name of feature (e.g., "hub-core").
            
        Returns:
            Dictionary with bundle content and metadata.
            
        Raises:
            ValueError: If feature not found.
        """
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        composition = []
        artifacts = []
        included_decisions: Set[str] = set()
        
        # Get feature intent
        feature = self.index["feature_intents"].get(feature_name)
        if not feature:
            raise ValueError(f"Feature intent not found: {feature_name}")
        
        artifacts.append({
            "type": "feature_intent",
            "path": feature["path"],
            "content": feature["content"],
            "name": feature_name,
        })
        composition.append(feature["path"])
        
        # Always include project intent
        project_intent = self.index.get("project_intent")
        if project_intent:
            artifacts.append({
                "type": "project_intent",
                "path": project_intent["path"],
                "content": project_intent["content"],
            })
            composition.append(project_intent["path"])
            
            # Include decisions linked by project intent
            project_links = self._extract_decision_links(project_intent["content"])
            included_decisions.update(project_links)
        
        # Include foundational decisions
        included_decisions.update(self.FOUNDATIONAL_DECISIONS)
        
        # Include decisions linked by feature
        feature_links = self._extract_decision_links(feature["content"])
        included_decisions.update(feature_links)
        
        # Add all included decisions
        for decision_num in sorted(included_decisions):
            decision = self.index["decisions"].get(decision_num)
            if decision:
                artifacts.append({
                    "type": "decision",
                    "path": decision["path"],
                    "content": decision["content"],
                    "number": decision_num,
                })
                composition.append(decision["path"])
        
        metadata = BundleMetadata(
            bundle_id=bundle_id,
            bundle_type="feature",
            identifier=feature_name,
            timestamp=timestamp,
            composition=sorted(composition),
        )
        
        return {
            "metadata": {
                "bundle_id": metadata.bundle_id,
                "bundle_type": metadata.bundle_type,
                "identifier": metadata.identifier,
                "timestamp": metadata.timestamp,
                "composition": metadata.composition,
            },
            "artifacts": artifacts,
        }
    
    def bundle_decision(self, decision_num: str) -> Dict:
        """Generate bundle for a decision.
        
        Per Decision 003:
        - Include: decision file
        - Include: decisions referenced in "Related" section
        - No intent inclusion (decisions don't reference features)
        
        Args:
            decision_num: Decision number (e.g., "001").
            
        Returns:
            Dictionary with bundle content and metadata.
            
        Raises:
            ValueError: If decision not found.
        """
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        composition = []
        artifacts = []
        included_decisions: Set[str] = {decision_num}
        
        # Get the decision
        decision = self.index["decisions"].get(decision_num)
        if not decision:
            raise ValueError(f"Decision not found: {decision_num}")
        
        artifacts.append({
            "type": "decision",
            "path": decision["path"],
            "content": decision["content"],
            "number": decision_num,
        })
        composition.append(decision["path"])
        
        # Include decisions referenced in "Related" section
        related_links = self._extract_decision_links(decision["content"])
        included_decisions.update(related_links)
        
        # Add all referenced decisions (excluding the root decision to avoid duplication)
        for ref_num in sorted(included_decisions):
            if ref_num != decision_num:
                ref_decision = self.index["decisions"].get(ref_num)
                if ref_decision:
                    artifacts.append({
                        "type": "decision",
                        "path": ref_decision["path"],
                        "content": ref_decision["content"],
                        "number": ref_num,
                    })
                    composition.append(ref_decision["path"])
        
        metadata = BundleMetadata(
            bundle_id=bundle_id,
            bundle_type="decision",
            identifier=decision_num,
            timestamp=timestamp,
            composition=sorted(composition),
        )
        
        return {
            "metadata": {
                "bundle_id": metadata.bundle_id,
                "bundle_type": metadata.bundle_type,
                "identifier": metadata.identifier,
                "timestamp": metadata.timestamp,
                "composition": metadata.composition,
            },
            "artifacts": artifacts,
        }
    
    def _extract_decision_links(self, content: str) -> Set[str]:
        """Extract decision numbers from markdown links.
        
        Finds patterns like:
        - [Decision: ...](../decisions/001-*.md)
        - [Decision: ...](001-*.md)
        
        Args:
            content: Markdown content to parse.
            
        Returns:
            Set of decision numbers (e.g., {"001", "003"}).
        """
        decision_nums = set()
        
        # Pattern 1: Relative path ../decisions/NNN-*.md
        pattern1 = r'\[Decision:[^\]]+\]\(\.\./decisions/(\d{3})-[^\)]+\.md\)'
        matches = re.findall(pattern1, content)
        decision_nums.update(matches)
        
        # Pattern 2: Same directory NNN-*.md
        pattern2 = r'\[Decision:[^\]]+\]\((\d{3})-[^\)]+\.md\)'
        matches = re.findall(pattern2, content)
        decision_nums.update(matches)
        
        return decision_nums
