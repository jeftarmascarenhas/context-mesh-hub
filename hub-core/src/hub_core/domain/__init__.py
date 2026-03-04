"""Domain layer package.

Contains business logic organized in:
- models/: Pure data structures (dataclasses, enums)
- services/: Business logic (testable, dependency-injected)
"""

from .models import (
    # Analysis
    AnalysisConfidenceLevel,
    Evidence,
    ProposedArtifact,
    StructuralAnalysis,
    SliceDefinition,
    # Build
    ApprovalStatus,
    ImplementationStep,
    BuildPlan,
    ApprovalState,
    ExecutionInstruction,
    # Learn
    LearningArtifactType,
    LearningConfidenceLevel,
    ImpactLevel,
    OutcomeSummary,
    LearningDraft,
    ContextUpdateProposal,
    ChangelogEntryProposal,
    LearningProposal,
)

__all__ = [
    # Analysis
    "AnalysisConfidenceLevel",
    "Evidence",
    "ProposedArtifact",
    "StructuralAnalysis",
    "SliceDefinition",
    # Build
    "ApprovalStatus",
    "ImplementationStep",
    "BuildPlan",
    "ApprovalState",
    "ExecutionInstruction",
    # Learn
    "LearningArtifactType",
    "LearningConfidenceLevel",
    "ImpactLevel",
    "OutcomeSummary",
    "LearningDraft",
    "ContextUpdateProposal",
    "ChangelogEntryProposal",
    "LearningProposal",
]
