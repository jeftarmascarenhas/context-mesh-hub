"""Domain models package.

Contains all dataclasses and enums representing core business entities.
Organized by domain area (artifacts, analysis, build, learn).
"""

# Analysis models (brownfield)
from .analysis import (
    ConfidenceLevel as AnalysisConfidenceLevel,
    Evidence,
    ProposedArtifact,
    StructuralAnalysis,
    SliceDefinition,
)

# Build models
from .build import (
    ApprovalStatus,
    ImplementationStep,
    BuildPlan,
    ApprovalState,
    ExecutionInstruction,
)

# Learn models
from .learn import (
    LearningArtifactType,
    ConfidenceLevel as LearningConfidenceLevel,
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
