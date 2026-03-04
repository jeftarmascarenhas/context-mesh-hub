"""Cross-reference validator.

Validates reference integrity between artifacts according to ARTIFACT_SPECS.md.
"""

import re
from pathlib import Path
from typing import Dict, Set, List

from .validation_result import ValidationResult


class CrossReferenceValidator:
    """Validates cross-references between artifacts."""
    
    def __init__(self, context_index: Dict):
        """Initialize validator.
        
        Args:
            context_index: Loaded context index from ContextLoader
        """
        self.index = context_index
    
    def validate_feature_references(self, feature_name: str, content: str, filepath: str) -> ValidationResult:
        """Validate references in a feature intent.
        
        Args:
            feature_name: Feature identifier
            content: Feature content
            filepath: Path to feature file
            
        Returns:
            ValidationResult with reference issues
        """
        result = ValidationResult()
        
        # Find decision references
        decision_refs = self._extract_decision_references(content)
        
        for decision_ref in decision_refs:
            if decision_ref not in self.index.get("decisions", {}):
                result.add_error(
                    f"Feature references non-existent decision: {decision_ref}",
                    artifact=filepath,
                    rule="broken_reference"
                )
        
        # Find feature references (cross-links to other features)
        feature_refs = self._extract_feature_references(content)
        
        for feature_ref in feature_refs:
            if feature_ref not in self.index.get("feature_intents", {}):
                result.add_error(
                    f"Feature references non-existent feature: {feature_ref}",
                    artifact=filepath,
                    rule="broken_reference"
                )
        
        return result
    
    def validate_decision_references(self, decision_num: str, content: str, filepath: str) -> ValidationResult:
        """Validate references in a decision.
        
        Args:
            decision_num: Decision number (e.g., "001")
            content: Decision content
            filepath: Path to decision file
            
        Returns:
            ValidationResult with reference issues
        """
        result = ValidationResult()
        
        # Find references to other decisions
        decision_refs = self._extract_decision_references(content)
        
        for decision_ref in decision_refs:
            if decision_ref != decision_num and decision_ref not in self.index.get("decisions", {}):
                result.add_error(
                    f"Decision {decision_num} references non-existent decision: {decision_ref}",
                    artifact=filepath,
                    rule="broken_reference"
                )
        
        # Find references to features
        feature_refs = self._extract_feature_references(content)
        
        for feature_ref in feature_refs:
            if feature_ref not in self.index.get("feature_intents", {}):
                result.add_warning(
                    f"Decision {decision_num} references non-existent feature: {feature_ref}",
                    artifact=filepath,
                    rule="broken_reference"
                )
        
        return result
    
    def validate_all_references(self) -> ValidationResult:
        """Validate all cross-references in the context.
        
        Returns:
            ValidationResult with all reference issues
        """
        result = ValidationResult()
        
        # Validate feature references
        for feature_name, feature in self.index.get("feature_intents", {}).items():
            feature_result = self.validate_feature_references(
                feature_name,
                feature.get("content", ""),
                feature.get("path", "")
            )
            result.merge(feature_result)
        
        # Validate decision references
        for decision_num, decision in self.index.get("decisions", {}).items():
            decision_result = self.validate_decision_references(
                decision_num,
                decision.get("content", ""),
                decision.get("path", "")
            )
            result.merge(decision_result)
        
        return result
    
    def _extract_decision_references(self, content: str) -> Set[str]:
        """Extract decision references from content.
        
        Looks for patterns like:
        - [Decision: ...](../decisions/D001-*.md)
        - [D001 - Name](./D001-*.md)
        - D001 (in text)
        
        Args:
            content: Markdown content
            
        Returns:
            Set of decision numbers (e.g., {"001", "042"})
        """
        decisions = set()
        
        # Pattern 1: [Decision: ...](../decisions/D001-*.md)
        pattern1 = r'\[Decision:[^\]]*\]\([^\)]*D(\d{3,4})-[^\)]*\.md\)'
        decisions.update(re.findall(pattern1, content))
        
        # Pattern 2: [D001 - Name](./D001-*.md)
        pattern2 = r'\[D(\d{3,4})[^\]]*\]\([^\)]*D\d{3,4}-[^\)]*\.md\)'
        decisions.update(re.findall(pattern2, content))
        
        # Pattern 3: D001 in text (be cautious with this)
        pattern3 = r'\bD(\d{3,4})\b'
        decisions.update(re.findall(pattern3, content))
        
        return decisions
    
    def _extract_feature_references(self, content: str) -> Set[str]:
        """Extract feature references from content.
        
        Looks for patterns like:
        - [Feature: ...](../intent/F001-*.md)
        - [F001 - Name](./F001-*.md)
        
        Args:
            content: Markdown content
            
        Returns:
            Set of feature identifiers (e.g., {"feature-001", "feature-042"})
        """
        features = set()
        
        # Pattern 1: [Feature: ...](../intent/F001-*.md) or [Feature: ...](./F001-*.md)
        pattern1 = r'\[Feature:[^\]]*\]\([^\)]*F(\d{3,4})-([^\)\/]+)\.md\)'
        matches1 = re.findall(pattern1, content)
        for num, slug in matches1:
            features.add(f"feature-{num}")
        
        # Pattern 2: [F001 - Name](./F001-*.md)
        pattern2 = r'\[F(\d{3,4})[^\]]*\]\([^\)]*F\d{3,4}-([^\)\/]+)\.md\)'
        matches2 = re.findall(pattern2, content)
        for num, slug in matches2:
            features.add(f"feature-{num}")
        
        return features
    
    def validate_circular_references(self) -> ValidationResult:
        """Check for circular reference chains (informational).
        
        Circular references are allowed but can be informational.
        
        Returns:
            ValidationResult with circular reference info
        """
        result = ValidationResult()
        
        # Build adjacency list
        graph = {}
        
        # Add features
        for feature_name, feature in self.index.get("feature_intents", {}).items():
            content = feature.get("content", "")
            refs = self._extract_feature_references(content)
            graph[f"F-{feature_name}"] = [f"F-{ref}" for ref in refs]
        
        # Add decisions
        for decision_num, decision in self.index.get("decisions", {}).items():
            content = decision.get("content", "")
            refs = self._extract_decision_references(content)
            graph[f"D-{decision_num}"] = [f"D-{ref}" for ref in refs]
        
        # Detect cycles (simple DFS approach)
        visited = set()
        rec_stack = set()
        
        def has_cycle(node, path):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, path + [neighbor]):
                        return True
                elif neighbor in rec_stack:
                    cycle_path = " -> ".join(path[path.index(neighbor):] + [neighbor])
                    result.add_info(
                        f"Circular reference detected: {cycle_path}",
                        rule="circular_reference"
                    )
                    return False  # Continue checking for other cycles
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                has_cycle(node, [node])
        
        return result
