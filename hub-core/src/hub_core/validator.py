"""Validation engine for Context Mesh structure and content integrity."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

from .loader import ContextLoader


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    level: str  # "error", "warning", "info"
    message: str
    artifact: Optional[str] = None  # Path or identifier of affected artifact


@dataclass
class ValidationResult:
    """Result of validation operation."""
    valid: bool
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    info: List[ValidationIssue] = field(default_factory=list)
    
    def add_error(self, message: str, artifact: Optional[str] = None):
        """Add an error issue."""
        self.errors.append(ValidationIssue("error", message, artifact))
        self.valid = False
    
    def add_warning(self, message: str, artifact: Optional[str] = None):
        """Add a warning issue."""
        self.warnings.append(ValidationIssue("warning", message, artifact))
    
    def add_info(self, message: str, artifact: Optional[str] = None):
        """Add an info issue."""
        self.info.append(ValidationIssue("info", message, artifact))


class ContextValidator:
    """Validates Context Mesh structure, content, and references."""
    
    # Required sections for different artifact types
    REQUIRED_SECTIONS = {
        "project_intent": ["What", "Why", "Scope", "Acceptance Criteria"],
        "feature_intent": ["What", "Why", "Scope", "Acceptance Criteria", "Related", "Status"],
        "decision": ["Context", "Decision", "Rationale", "Status"],
    }
    
    def __init__(self, loader: ContextLoader):
        """Initialize validator with a context loader.
        
        Args:
            loader: ContextLoader instance with loaded index.
        """
        self.loader = loader
        self.repo_root = loader.repo_root
        self.context_dir = loader.context_dir
    
    def validate(self) -> ValidationResult:
        """Run all validation checks.
        
        Returns:
            ValidationResult with all issues found.
        """
        result = ValidationResult(valid=True)
        
        # Structure validation
        self._validate_structure(result)
        
        # Content validation
        self._validate_content(result)
        
        # Reference validation
        self._validate_references(result)
        
        return result
    
    def _validate_structure(self, result: ValidationResult):
        """Validate required directory structure."""
        # Check context/ directory exists
        if not self.context_dir.exists():
            result.add_error(
                f"Context directory not found: {self.context_dir}",
                "context/"
            )
            return  # Can't continue without context directory
        
        # Check required subdirectories
        required_dirs = {
            "intent": self.context_dir / "intent",
            "decisions": self.context_dir / "decisions",
            "evolution": self.context_dir / "evolution",
        }
        
        for name, path in required_dirs.items():
            if not path.exists():
                result.add_error(
                    f"Required directory missing: context/{name}/",
                    f"context/{name}/"
                )
        
        # Check AGENTS.md at root
        agents_md = self.repo_root / "AGENTS.md"
        if not agents_md.exists():
            result.add_error(
                "AGENTS.md not found at repository root",
                "AGENTS.md"
            )
        
        # Check .context-mesh-framework.md
        framework_md = self.context_dir / ".context-mesh-framework.md"
        if not framework_md.exists():
            result.add_error(
                "context/.context-mesh-framework.md not found",
                "context/.context-mesh-framework.md"
            )
    
    def _validate_content(self, result: ValidationResult):
        """Validate required sections in context files."""
        index = self.loader.index
        
        # Validate project intent
        project_intent = index.get("project_intent")
        if project_intent:
            self._check_required_sections(
                result,
                project_intent["content"],
                "project_intent",
                project_intent["path"]
            )
        else:
            result.add_error(
                "Project intent not found: context/intent/project-intent.md",
                "context/intent/project-intent.md"
            )
        
        # Validate feature intents
        for name, feature in index["feature_intents"].items():
            self._check_required_sections(
                result,
                feature["content"],
                "feature_intent",
                feature["path"]
            )
        
        # Validate decisions
        for num, decision in index["decisions"].items():
            self._check_required_sections(
                result,
                decision["content"],
                "decision",
                decision["path"]
            )
    
    def _check_required_sections(
        self,
        result: ValidationResult,
        content: str,
        artifact_type: str,
        artifact_path: str
    ):
        """Check if content has required sections.
        
        Args:
            result: ValidationResult to add issues to.
            content: Markdown content to check.
            artifact_type: Type of artifact (project_intent, feature_intent, decision).
            artifact_path: Path to artifact for error reporting.
        """
        required = self.REQUIRED_SECTIONS.get(artifact_type, [])
        
        for section in required:
            # Look for markdown headers (## Section Name or ### Section Name)
            pattern = rf"^#{{2,3}}\s+{re.escape(section)}\s*$"
            if not re.search(pattern, content, re.MULTILINE):
                result.add_error(
                    f"Missing required section '{section}' in {artifact_type}",
                    artifact_path
                )
    
    def _validate_references(self, result: ValidationResult):
        """Validate reference integrity (links resolve correctly)."""
        index = self.loader.index
        
        # Validate feature intent references
        for name, feature in index["feature_intents"].items():
            self._validate_feature_references(result, feature, name)
        
        # Validate decision references
        for num, decision in index["decisions"].items():
            self._validate_decision_references(result, decision, num)
    
    def _validate_feature_references(
        self,
        result: ValidationResult,
        feature: Dict,
        feature_name: str
    ):
        """Validate references in a feature intent."""
        content = feature["content"]
        
        # Find all decision references: [Decision: ...](../decisions/NNN-*.md)
        decision_refs = re.findall(
            r'\[Decision:[^\]]+\]\(\.\./decisions/(\d{3})-[^\)]+\.md\)',
            content
        )
        
        for decision_num in decision_refs:
            if decision_num not in self.loader.index["decisions"]:
                result.add_error(
                    f"Feature '{feature_name}' references missing decision: {decision_num}",
                    feature["path"]
                )
        
        # Find project intent reference
        if "[Project Intent]" in content:
            project_ref = re.search(
                r'\[Project Intent\]\(\./project-intent\.md\)',
                content
            )
            if project_ref and not self.loader.index.get("project_intent"):
                result.add_warning(
                    f"Feature '{feature_name}' references project intent, but it's missing",
                    feature["path"]
                )
    
    def _validate_decision_references(
        self,
        result: ValidationResult,
        decision: Dict,
        decision_num: str
    ):
        """Validate references in a decision."""
        content = decision["content"]
        
        # Find references to other decisions
        decision_refs = re.findall(
            r'\[Decision:[^\]]+\]\((\d{3})-[^\)]+\.md\)',
            content
        )
        
        for ref_num in decision_refs:
            if ref_num not in self.loader.index["decisions"]:
                result.add_warning(
                    f"Decision {decision_num} references missing decision: {ref_num}",
                    decision["path"]
                )
        
        # Find references to features (should be rare, but validate if present)
        feature_refs = re.findall(
            r'\[Feature:[^\]]+\]\(\.\./intent/feature-([^\)]+)\.md\)',
            content
        )
        
        for feature_name in feature_refs:
            if feature_name not in self.loader.index["feature_intents"]:
                result.add_warning(
                    f"Decision {decision_num} references missing feature: {feature_name}",
                    decision["path"]
                )
    
    def validate_structure(self) -> ValidationResult:
        """Validate only structure (quick check)."""
        result = ValidationResult(valid=True)
        self._validate_structure(result)
        return result
    
    def validate_content(self) -> ValidationResult:
        """Validate only content sections."""
        result = ValidationResult(valid=True)
        self._validate_content(result)
        return result
    
    def validate_references(self) -> ValidationResult:
        """Validate only references."""
        result = ValidationResult(valid=True)
        self._validate_references(result)
        return result
