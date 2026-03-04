"""Domain validation module.

Provides validation rules and validators for Context Mesh artifacts
based on ARTIFACT_SPECS.md specifications.
"""

from .validation_result import ValidationResult, ValidationIssue
from .artifact_validators import (
    FeatureValidator,
    DecisionValidator,
    PatternValidator,
    AntiPatternValidator,
    ProjectIntentValidator,
    AgentValidator,
)
from .naming_validator import NamingValidator
from .cross_reference_validator import CrossReferenceValidator

__all__ = [
    "ValidationResult",
    "ValidationIssue",
    "FeatureValidator",
    "DecisionValidator",
    "PatternValidator",
    "AntiPatternValidator",
    "ProjectIntentValidator",
    "AgentValidator",
    "NamingValidator",
    "CrossReferenceValidator",
]
