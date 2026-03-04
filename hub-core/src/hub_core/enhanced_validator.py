"""Enhanced validation service.

Comprehensive validation service that validates Context Mesh artifacts
against ARTIFACT_SPECS.md specifications.
"""

from pathlib import Path
from typing import Dict, Optional

from .loader import ContextLoader
from .infrastructure.parsers.markdown_parser import MarkdownParser
from .domain.validation import (
    ValidationResult,
    FeatureValidator,
    DecisionValidator,
    ProjectIntentValidator,
    PatternValidator,
    AntiPatternValidator,
    AgentValidator,
    NamingValidator,
    CrossReferenceValidator,
)


class EnhancedContextValidator:
    """Enhanced validator for Context Mesh artifacts.
    
    Validates:
    - Naming conventions (F00X-*.md, D00X-*.md)
    - Required sections (What, Why, Acceptance Criteria, etc.)
    - Status field format (Active | Completed | Replaced | Abandoned)
    - Cross-references (links to decisions/features)
    - File structure and organization
    """
    
    def __init__(self, loader: ContextLoader, parser: MarkdownParser = None):
        """Initialize enhanced validator.
        
        Args:
            loader: ContextLoader with loaded index
            parser: Optional MarkdownParser instance
        """
        self.loader = loader
        self.parser = parser or MarkdownParser()
        self.repo_root = loader.repo_root
        self.context_dir = loader.context_dir
        
        # Initialize artifact validators
        self.feature_validator = FeatureValidator(self.parser)
        self.decision_validator = DecisionValidator(self.parser)
        self.project_intent_validator = ProjectIntentValidator(self.parser)
        self.pattern_validator = PatternValidator(self.parser)
        self.anti_pattern_validator = AntiPatternValidator(self.parser)
        self.agent_validator = AgentValidator(self.parser)
        
        # Initialize cross-reference validator
        self.cross_ref_validator = CrossReferenceValidator(loader.index)
    
    def validate(self) -> ValidationResult:
        """Run comprehensive validation.
        
        Validates:
        1. Directory structure
        2. File naming conventions
        3. Required sections in artifacts
        4. Status fields
        5. Cross-references
        6. General best practices
        
        Returns:
            ValidationResult with all issues found
        """
        result = ValidationResult()
        
        # 1. Validate structure
        structure_result = self.validate_structure()
        result.merge(structure_result)
        
        # 2. Validate naming conventions
        naming_result = self.validate_naming()
        result.merge(naming_result)
        
        # 3. Validate content
        content_result = self.validate_content()
        result.merge(content_result)
        
        # 4. Validate cross-references
        ref_result = self.validate_references()
        result.merge(ref_result)
        
        # 5. Check for circular references (informational)
        circular_result = self.cross_ref_validator.validate_circular_references()
        result.merge(circular_result)
        
        return result
    
    def validate_structure(self) -> ValidationResult:
        """Validate required directory structure.
        
        Returns:
            ValidationResult with structure issues
        """
        result = ValidationResult()
        
        # Check context/ directory exists
        if not self.context_dir.exists():
            result.add_error(
                f"Context directory not found: {self.context_dir}",
                artifact="context/",
                rule="required_directory"
            )
            return result
        
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
                    artifact=f"context/{name}/",
                    rule="required_directory"
                )
        
        # Check optional but recommended directories
        optional_dirs = {
            "knowledge": self.context_dir / "knowledge",
            "agents": self.context_dir / "agents",
        }
        
        for name, path in optional_dirs.items():
            if not path.exists():
                result.add_info(
                    f"Optional directory missing: context/{name}/",
                    artifact=f"context/{name}/",
                    rule="optional_directory"
                )
        
        # Check AGENTS.md at root
        agents_md = self.repo_root / "AGENTS.md"
        if not agents_md.exists():
            result.add_error(
                "AGENTS.md not found at repository root",
                artifact="AGENTS.md",
                rule="required_file"
            )
        
        # Check project-intent.md
        project_intent_path = self.context_dir / "intent" / "project-intent.md"
        if not project_intent_path.exists():
            result.add_error(
                "project-intent.md not found in context/intent/",
                artifact="context/intent/project-intent.md",
                rule="required_file"
            )
        
        # Check changelog.md
        changelog_path = self.context_dir / "evolution" / "changelog.md"
        if not changelog_path.exists():
            result.add_warning(
                "changelog.md not found in context/evolution/",
                artifact="context/evolution/changelog.md",
                rule="recommended_file"
            )
        
        return result
    
    def validate_naming(self) -> ValidationResult:
        """Validate file naming conventions.
        
        Returns:
            ValidationResult with naming issues
        """
        result = ValidationResult()
        
        # Validate feature names
        for feature_name, feature in self.loader.index.get("feature_intents", {}).items():
            filepath = feature.get("path", "")
            filename = Path(filepath).name if filepath else feature_name
            
            naming_result = NamingValidator.validate_feature_name(filename, filepath)
            result.merge(naming_result)
        
        # Validate decision names
        for decision_num, decision in self.loader.index.get("decisions", {}).items():
            filepath = decision.get("path", "")
            filename = Path(filepath).name if filepath else f"D{decision_num}"
            
            naming_result = NamingValidator.validate_decision_name(filename, filepath)
            result.merge(naming_result)
        
        # Validate agent names (if agents exist)
        agents_dir = self.context_dir / "agents"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.md"):
                naming_result = NamingValidator.validate_agent_name(agent_file.name, str(agent_file))
                result.merge(naming_result)
        
        # Validate pattern names
        patterns_dir = self.context_dir / "knowledge" / "patterns"
        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("*.md"):
                naming_result = NamingValidator.validate_pattern_name(pattern_file.name, str(pattern_file))
                result.merge(naming_result)
        
        # Validate anti-pattern names
        anti_patterns_dir = self.context_dir / "knowledge" / "anti-patterns"
        if anti_patterns_dir.exists():
            for anti_pattern_file in anti_patterns_dir.glob("*.md"):
                naming_result = NamingValidator.validate_pattern_name(anti_pattern_file.name, str(anti_pattern_file))
                result.merge(naming_result)
        
        return result
    
    def validate_content(self) -> ValidationResult:
        """Validate content structure and required sections.
        
        Returns:
            ValidationResult with content issues
        """
        result = ValidationResult()
        
        # Validate project intent
        project_intent = self.loader.index.get("project_intent")
        if project_intent:
            content = project_intent.get("content", "")
            filepath = project_intent.get("path", "")
            
            intent_result = self.project_intent_validator.validate(content, filepath)
            result.merge(intent_result)
        
        # Validate features
        for feature_name, feature in self.loader.index.get("feature_intents", {}).items():
            content = feature.get("content", "")
            filepath = feature.get("path", "")
            
            feature_result = self.feature_validator.validate(content, filepath)
            result.merge(feature_result)
        
        # Validate decisions
        for decision_num, decision in self.loader.index.get("decisions", {}).items():
            content = decision.get("content", "")
            filepath = decision.get("path", "")
            
            decision_result = self.decision_validator.validate(content, filepath)
            result.merge(decision_result)
        
        # Validate agents
        agents_dir = self.context_dir / "agents"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("agent-*.md"):
                content = agent_file.read_text(encoding="utf-8")
                agent_result = self.agent_validator.validate(content, str(agent_file))
                result.merge(agent_result)
        
        # Validate patterns
        patterns_dir = self.context_dir / "knowledge" / "patterns"
        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("*.md"):
                content = pattern_file.read_text(encoding="utf-8")
                pattern_result = self.pattern_validator.validate(content, str(pattern_file))
                result.merge(pattern_result)
        
        # Validate anti-patterns
        anti_patterns_dir = self.context_dir / "knowledge" / "anti-patterns"
        if anti_patterns_dir.exists():
            for anti_pattern_file in anti_patterns_dir.glob("*.md"):
                content = anti_pattern_file.read_text(encoding="utf-8")
                anti_pattern_result = self.anti_pattern_validator.validate(content, str(anti_pattern_file))
                result.merge(anti_pattern_result)
        
        return result
    
    def validate_references(self) -> ValidationResult:
        """Validate cross-references between artifacts.
        
        Returns:
            ValidationResult with reference issues
        """
        return self.cross_ref_validator.validate_all_references()
    
    def validate_artifact(
        self,
        artifact_type: str,
        content: str,
        filepath: str
    ) -> ValidationResult:
        """Validate a single artifact.
        
        Args:
            artifact_type: Type of artifact (feature, decision, pattern, etc.)
            content: Artifact content
            filepath: Path to artifact
            
        Returns:
            ValidationResult for the artifact
        """
        if artifact_type == "feature":
            return self.feature_validator.validate(content, filepath)
        elif artifact_type == "decision":
            return self.decision_validator.validate(content, filepath)
        elif artifact_type == "project_intent":
            return self.project_intent_validator.validate(content, filepath)
        elif artifact_type == "pattern":
            return self.pattern_validator.validate(content, filepath)
        elif artifact_type == "anti_pattern":
            return self.anti_pattern_validator.validate(content, filepath)
        elif artifact_type == "agent":
            return self.agent_validator.validate(content, filepath)
        else:
            result = ValidationResult()
            result.add_warning(
                f"Unknown artifact type: {artifact_type}",
                artifact=filepath,
                rule="unknown_type"
            )
            return result
