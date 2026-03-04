"""Naming convention validators.

Validates artifact file naming according to ARTIFACT_SPECS.md.
"""

import re
from pathlib import Path
from typing import Optional

from .validation_result import ValidationResult


class NamingValidator:
    """Validates naming conventions for Context Mesh artifacts."""
    
    # Naming patterns from ARTIFACT_SPECS.md
    FEATURE_PATTERN = re.compile(r'^F\d{3,4}-.+\.md$')
    DECISION_PATTERN = re.compile(r'^D\d{3,4}-.+\.md$')
    AGENT_PATTERN = re.compile(r'^agent-.+\.md$')
    PATTERN_FILE = re.compile(r'^[a-z0-9-]+\.md$')
    
    @staticmethod
    def validate_feature_name(filename: str, filepath: Optional[str] = None) -> ValidationResult:
        """Validate feature file naming convention.
        
        Format: F00X-description.md where X is sequential number
        - Must start with F followed by 3-4 digits
        - Use lowercase with hyphens for description
        
        Args:
            filename: File name to validate
            filepath: Full path for error reporting
            
        Returns:
            ValidationResult with any naming issues
        """
        result = ValidationResult()
        
        if not NamingValidator.FEATURE_PATTERN.match(filename):
            result.add_error(
                f"Invalid feature naming: '{filename}'. Must follow F00X-description.md format",
                artifact=filepath or filename,
                rule="naming_convention"
            )
            return result
        
        # Extract number part
        num_match = re.match(r'^F(\d{3,4})-', filename)
        if num_match:
            num = num_match.group(1)
            if not num.startswith('00') and len(num) == 3:
                result.add_warning(
                    f"Feature numbering should start with F001, F002, etc. Got: {filename}",
                    artifact=filepath or filename,
                    rule="naming_convention"
                )
        
        # Check description uses lowercase and hyphens
        desc_match = re.match(r'^F\d{3,4}-([^.]+)\.md$', filename)
        if desc_match:
            description = desc_match.group(1)
            if description != description.lower():
                result.add_warning(
                    f"Feature description should use lowercase: '{description}'",
                    artifact=filepath or filename,
                    rule="naming_convention"
                )
            if '_' in description:
                result.add_warning(
                    f"Feature description should use hyphens, not underscores: '{description}'",
                    artifact=filepath or filename,
                    rule="naming_convention"
                )
        
        return result
    
    @staticmethod
    def validate_decision_name(filename: str, filepath: Optional[str] = None) -> ValidationResult:
        """Validate decision file naming convention.
        
        Format: D00X-description.md where X is sequential number
        - Must start with D followed by 3-4 digits
        - Use lowercase with hyphens for description
        
        Args:
            filename: File name to validate
            filepath: Full path for error reporting
            
        Returns:
            ValidationResult with any naming issues
        """
        result = ValidationResult()
        
        if not NamingValidator.DECISION_PATTERN.match(filename):
            result.add_error(
                f"Invalid decision naming: '{filename}'. Must follow D00X-description.md format",
                artifact=filepath or filename,
                rule="naming_convention"
            )
            return result
        
        # Extract number part
        num_match = re.match(r'^D(\d{3,4})-', filename)
        if num_match:
            num = num_match.group(1)
            if not num.startswith('00') and len(num) == 3:
                result.add_warning(
                    f"Decision numbering should start with D001, D002, etc. Got: {filename}",
                    artifact=filepath or filename,
                    rule="naming_convention"
                )
        
        # Check description uses lowercase and hyphens
        desc_match = re.match(r'^D\d{3,4}-([^.]+)\.md$', filename)
        if desc_match:
            description = desc_match.group(1)
            if description != description.lower():
                result.add_warning(
                    f"Decision description should use lowercase: '{description}'",
                    artifact=filepath or filename,
                    rule="naming_convention"
                )
            if '_' in description:
                result.add_warning(
                    f"Decision description should use hyphens, not underscores: '{description}'",
                    artifact=filepath or filename,
                    rule="naming_convention"
                )
        
        return result
    
    @staticmethod
    def validate_agent_name(filename: str, filepath: Optional[str] = None) -> ValidationResult:
        """Validate agent file naming convention.
        
        Format: agent-descriptive-name.md
        
        Args:
            filename: File name to validate
            filepath: Full path for error reporting
            
        Returns:
            ValidationResult with any naming issues
        """
        result = ValidationResult()
        
        if not NamingValidator.AGENT_PATTERN.match(filename):
            result.add_error(
                f"Invalid agent naming: '{filename}'. Must follow agent-description.md format",
                artifact=filepath or filename,
                rule="naming_convention"
            )
        
        return result
    
    @staticmethod
    def validate_pattern_name(filename: str, filepath: Optional[str] = None) -> ValidationResult:
        """Validate pattern/anti-pattern file naming convention.
        
        Format: descriptive-name.md (lowercase with hyphens)
        
        Args:
            filename: File name to validate
            filepath: Full path for error reporting
            
        Returns:
            ValidationResult with any naming issues
        """
        result = ValidationResult()
        
        if not NamingValidator.PATTERN_FILE.match(filename):
            result.add_error(
                f"Invalid pattern naming: '{filename}'. Use lowercase with hyphens",
                artifact=filepath or filename,
                rule="naming_convention"
            )
        
        return result
    
    @staticmethod
    def extract_feature_number(filename: str) -> Optional[str]:
        """Extract feature number from filename.
        
        Args:
            filename: Feature filename (e.g., F001-auth.md)
            
        Returns:
            Feature number (e.g., "001") or None if invalid
        """
        match = re.match(r'^F(\d{3,4})-', filename)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_decision_number(filename: str) -> Optional[str]:
        """Extract decision number from filename.
        
        Args:
            filename: Decision filename (e.g., D001-tech-stack.md)
            
        Returns:
            Decision number (e.g., "001") or None if invalid
        """
        match = re.match(r'^D(\d{3,4})-', filename)
        return match.group(1) if match else None
