"""Artifact-specific validators.

Validates content structure for different artifact types according to ARTIFACT_SPECS.md.
"""

import re
from typing import List, Dict, Any

from ...infrastructure.parsers.markdown_parser import MarkdownParser
from .validation_result import ValidationResult


class ArtifactValidator:
    """Base class for artifact validators."""
    
    def __init__(self, parser: MarkdownParser = None):
        """Initialize validator.
        
        Args:
            parser: MarkdownParser instance for content extraction
        """
        self.parser = parser or MarkdownParser()
    
    def _validate_section_exists(
        self,
        result: ValidationResult,
        content: str,
        section_name: str,
        artifact_path: str,
        required: bool = True
    ):
        """Check if a section exists in content.
        
        Args:
            result: ValidationResult to add issues to
            content: Markdown content
            section_name: Section heading to look for
            artifact_path: Path for error reporting
            required: If True, missing section is error; otherwise warning
        """
        section_content = self.parser.extract_section(content, section_name)
        
        if not section_content:
            if required:
                result.add_error(
                    f"Missing required section: '{section_name}'",
                    artifact=artifact_path,
                    rule="required_section",
                    section=section_name
                )
            else:
                result.add_warning(
                    f"Recommended section missing: '{section_name}'",
                    artifact=artifact_path,
                    rule="recommended_section",
                    section=section_name
                )
    
    def _validate_status_field(
        self,
        result: ValidationResult,
        content: str,
        artifact_path: str,
        valid_statuses: List[str]
    ):
        """Validate Status field format and value.
        
        Args:
            result: ValidationResult to add issues to
            content: Markdown content
            artifact_path: Path for error reporting
            valid_statuses: List of valid status values
        """
        # Check for Status section
        if not re.search(r'##\s+Status', content, re.MULTILINE):
            result.add_error(
                "Missing required 'Status' section",
                artifact=artifact_path,
                rule="required_section",
                section="Status"
            )
            return
        
        # Check for Created date
        if not re.search(r'[-*]\s*\*\*Created\*\*:\s*\d{4}-\d{2}-\d{2}', content):
            result.add_error(
                "Missing 'Created' date in Status section (format: YYYY-MM-DD)",
                artifact=artifact_path,
                rule="status_field",
                section="Status"
            )
        
        # Check for Status value
        status_match = re.search(r'[-*]\s*\*\*Status\*\*:\s*(.+)$', content, re.MULTILINE)
        if not status_match:
            result.add_error(
                "Missing 'Status' field in Status section",
                artifact=artifact_path,
                rule="status_field",
                section="Status"
            )
        else:
            status_value = status_match.group(1).strip()
            # Extract first word (in case of "Superseded by D042" etc.)
            status_first_word = status_value.split()[0] if status_value else ""
            
            if status_first_word not in valid_statuses:
                result.add_error(
                    f"Invalid status value: '{status_value}'. Must be one of: {', '.join(valid_statuses)}",
                    artifact=artifact_path,
                    rule="status_field",
                    section="Status"
                )
    
    def _validate_cross_references(
        self,
        result: ValidationResult,
        content: str,
        artifact_path: str
    ):
        """Validate that cross-references use relative paths.
        
        Args:
            result: ValidationResult to add issues to
            content: Markdown content
            artifact_path: Path for error reporting
        """
        # Find all markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        
        for link_text, link_path in links:
            # Skip external URLs
            if link_path.startswith('http://') or link_path.startswith('https://'):
                continue
            
            # Skip anchors
            if link_path.startswith('#'):
                continue
            
            # Check if using relative path
            if link_path.startswith('/'):
                result.add_warning(
                    f"Use relative paths instead of absolute: '{link_path}'",
                    artifact=artifact_path,
                    rule="relative_paths"
                )


class FeatureValidator(ArtifactValidator):
    """Validates feature intent artifacts (F00X-*.md)."""
    
    REQUIRED_SECTIONS = ["What", "Why", "Acceptance Criteria", "Status"]
    RECOMMENDED_SECTIONS = ["How", "Related"]
    VALID_STATUSES = ["Active", "Completed", "Replaced", "Abandoned"]
    
    def validate(self, content: str, artifact_path: str) -> ValidationResult:
        """Validate feature intent content.
        
        Args:
            content: Feature markdown content
            artifact_path: Path to feature file
            
        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult()
        
        # Required sections
        for section in self.REQUIRED_SECTIONS:
            if section == "Status":
                self._validate_status_field(result, content, artifact_path, self.VALID_STATUSES)
            else:
                self._validate_section_exists(result, content, section, artifact_path, required=True)
        
        # Recommended sections
        for section in self.RECOMMENDED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=False)
        
        # Validate Acceptance Criteria format (should have checkboxes)
        ac_content = self.parser.extract_section(content, "Acceptance Criteria")
        if ac_content:
            # Check for checkbox format
            if not re.search(r'[-*]\s*\[[x\s]\]', ac_content):
                result.add_warning(
                    "Acceptance Criteria should use checkbox format: - [ ] criterion",
                    artifact=artifact_path,
                    rule="acceptance_criteria_format",
                    section="Acceptance Criteria"
                )
            
            # Check that there are criteria
            criteria = self.parser.extract_list_items(content, "Acceptance Criteria")
            if len(criteria) == 0:
                result.add_error(
                    "Acceptance Criteria section is empty - must have at least one criterion",
                    artifact=artifact_path,
                    rule="acceptance_criteria_empty",
                    section="Acceptance Criteria"
                )
        
        # Validate cross-references
        self._validate_cross_references(result, content, artifact_path)
        
        return result


class DecisionValidator(ArtifactValidator):
    """Validates decision artifacts (D00X-*.md)."""
    
    REQUIRED_SECTIONS = ["Context", "Decision", "Rationale", "Status"]
    RECOMMENDED_SECTIONS = ["Alternatives Considered", "Consequences", "Related"]
    VALID_STATUSES = ["Proposed", "Accepted", "Superseded", "Deprecated"]
    
    def validate(self, content: str, artifact_path: str) -> ValidationResult:
        """Validate decision content.
        
        Args:
            content: Decision markdown content
            artifact_path: Path to decision file
            
        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult()
        
        # Required sections
        for section in self.REQUIRED_SECTIONS:
            if section == "Status":
                self._validate_status_field(result, content, artifact_path, self.VALID_STATUSES)
            else:
                self._validate_section_exists(result, content, section, artifact_path, required=True)
        
        # Recommended sections
        for section in self.RECOMMENDED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=False)
        
        # Validate cross-references
        self._validate_cross_references(result, content, artifact_path)
        
        return result


class ProjectIntentValidator(ArtifactValidator):
    """Validates project intent (project-intent.md)."""
    
    REQUIRED_SECTIONS = ["What", "Why", "Scope", "Acceptance Criteria", "Status"]
    RECOMMENDED_SECTIONS = ["Constraints", "Related"]
    
    def validate(self, content: str, artifact_path: str) -> ValidationResult:
        """Validate project intent content.
        
        Args:
            content: Project intent markdown content
            artifact_path: Path to project-intent.md
            
        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult()
        
        # Required sections
        for section in self.REQUIRED_SECTIONS:
            if section == "Status":
                # Project intent should have Created date and Active status
                self._validate_status_field(result, content, artifact_path, ["Active"])
            else:
                self._validate_section_exists(result, content, section, artifact_path, required=True)
        
        # Recommended sections
        for section in self.RECOMMENDED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=False)
        
        # Validate cross-references
        self._validate_cross_references(result, content, artifact_path)
        
        return result


class PatternValidator(ArtifactValidator):
    """Validates pattern artifacts."""
    
    REQUIRED_SECTIONS = ["Context", "The Pattern", "Evidence", "Status"]
    RECOMMENDED_SECTIONS = ["When to Use", "When NOT to Use", "Implementation Guide", "Related"]
    
    def validate(self, content: str, artifact_path: str) -> ValidationResult:
        """Validate pattern content.
        
        Args:
            content: Pattern markdown content
            artifact_path: Path to pattern file
            
        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult()
        
        # Required sections
        for section in self.REQUIRED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=True)
        
        # Recommended sections
        for section in self.RECOMMENDED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=False)
        
        # Validate Status includes confidence and impact
        status_section = self.parser.extract_section(content, "Status")
        if status_section:
            if "Confidence:" not in status_section:
                result.add_warning(
                    "Status should include Confidence field (Low | Medium | High)",
                    artifact=artifact_path,
                    rule="status_field",
                    section="Status"
                )
            if "Impact:" not in status_section:
                result.add_warning(
                    "Status should include Impact field (Low | Medium | High)",
                    artifact=artifact_path,
                    rule="status_field",
                    section="Status"
                )
        
        # Validate cross-references
        self._validate_cross_references(result, content, artifact_path)
        
        return result


class AntiPatternValidator(ArtifactValidator):
    """Validates anti-pattern artifacts."""
    
    REQUIRED_SECTIONS = ["Context", "The Problem", "Evidence", "Recommendation", "Status"]
    RECOMMENDED_SECTIONS = ["Why It Happens", "Related"]
    
    def validate(self, content: str, artifact_path: str) -> ValidationResult:
        """Validate anti-pattern content.
        
        Args:
            content: Anti-pattern markdown content
            artifact_path: Path to anti-pattern file
            
        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult()
        
        # Required sections
        for section in self.REQUIRED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=True)
        
        # Recommended sections
        for section in self.RECOMMENDED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=False)
        
        # Validate Status includes confidence and impact
        status_section = self.parser.extract_section(content, "Status")
        if status_section:
            if "Confidence:" not in status_section:
                result.add_warning(
                    "Status should include Confidence field (Low | Medium | High)",
                    artifact=artifact_path,
                    rule="status_field",
                    section="Status"
                )
            if "Impact:" not in status_section:
                result.add_warning(
                    "Status should include Impact field (Low | Medium | High)",
                    artifact=artifact_path,
                    rule="status_field",
                    section="Status"
                )
        
        # Validate cross-references
        self._validate_cross_references(result, content, artifact_path)
        
        return result


class AgentValidator(ArtifactValidator):
    """Validates agent artifacts."""
    
    REQUIRED_SECTIONS = ["Purpose", "Context Files to Load", "Steps", "Definition of Done"]
    RECOMMENDED_SECTIONS = ["Constraints", "Related"]
    
    def validate(self, content: str, artifact_path: str) -> ValidationResult:
        """Validate agent content.
        
        Args:
            content: Agent markdown content
            artifact_path: Path to agent file
            
        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult()
        
        # Required sections
        for section in self.REQUIRED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=True)
        
        # Recommended sections
        for section in self.RECOMMENDED_SECTIONS:
            self._validate_section_exists(result, content, section, artifact_path, required=False)
        
        # Validate Definition of Done has checkboxes
        dod_content = self.parser.extract_section(content, "Definition of Done")
        if dod_content and not re.search(r'[-*]\s*\[[x\s]\]', dod_content):
            result.add_warning(
                "Definition of Done should use checkbox format: - [ ] criterion",
                artifact=artifact_path,
                rule="dod_format",
                section="Definition of Done"
            )
        
        # Validate cross-references
        self._validate_cross_references(result, content, artifact_path)
        
        return result
