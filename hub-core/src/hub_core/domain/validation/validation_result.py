"""Validation result structures.

Core data structures for validation results following ARTIFACT_SPECS.md.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationIssue:
    """Represents a validation issue.
    
    Attributes:
        level: Issue severity - "error", "warning", or "info"
        message: Description of the issue
        artifact: Path or identifier of affected artifact
        rule: Validation rule identifier (e.g., "naming_convention", "required_section")
        section: Section name where issue was found (optional)
    """
    level: str
    message: str
    artifact: Optional[str] = None
    rule: Optional[str] = None
    section: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "level": self.level,
            "message": self.message,
            "artifact": self.artifact,
            "rule": self.rule,
            "section": self.section,
        }


@dataclass
class ValidationResult:
    """Result of validation operation.
    
    Attributes:
        valid: True if no errors found
        errors: Critical issues that must be fixed
        warnings: Recommended improvements
        info: Informational messages
    """
    valid: bool = True
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    info: List[ValidationIssue] = field(default_factory=list)
    
    def add_error(self, message: str, artifact: Optional[str] = None, 
                  rule: Optional[str] = None, section: Optional[str] = None):
        """Add an error issue.
        
        Args:
            message: Error description
            artifact: Affected artifact path
            rule: Validation rule identifier
            section: Section where issue was found
        """
        self.errors.append(ValidationIssue(
            level="error",
            message=message,
            artifact=artifact,
            rule=rule,
            section=section,
        ))
        self.valid = False
    
    def add_warning(self, message: str, artifact: Optional[str] = None,
                    rule: Optional[str] = None, section: Optional[str] = None):
        """Add a warning issue.
        
        Args:
            message: Warning description
            artifact: Affected artifact path
            rule: Validation rule identifier
            section: Section where issue was found
        """
        self.warnings.append(ValidationIssue(
            level="warning",
            message=message,
            artifact=artifact,
            rule=rule,
            section=section,
        ))
    
    def add_info(self, message: str, artifact: Optional[str] = None,
                 rule: Optional[str] = None, section: Optional[str] = None):
        """Add an info issue.
        
        Args:
            message: Info description
            artifact: Affected artifact path
            rule: Validation rule identifier
            section: Section where issue was found
        """
        self.info.append(ValidationIssue(
            level="info",
            message=message,
            artifact=artifact,
            rule=rule,
            section=section,
        ))
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result into this one.
        
        Args:
            other: ValidationResult to merge
        """
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        if not other.valid:
            self.valid = False
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "info": [i.to_dict() for i in self.info],
        }
