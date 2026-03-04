"""Learn domain models.

Models for learning sync workflow (collect outcomes, classify learnings, apply).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class LearningArtifactType(Enum):
    """Types of learning artifacts per Decision 008."""
    DECISION_UPDATE = "decision_update"
    PATTERN = "pattern"
    ANTI_PATTERN = "anti_pattern"
    CONSTRAINT_DISCOVERY = "constraint_discovery"
    RISK_ANNOTATION = "risk_annotation"
    EVOLUTION_NOTE = "evolution_note"


class ConfidenceLevel(Enum):
    """Confidence level for learning artifacts."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImpactLevel(Enum):
    """Impact level for learning artifacts."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class OutcomeSummary:
    """Summary of execution outcomes."""
    what_implemented: List[str] = field(default_factory=list)
    what_failed: List[str] = field(default_factory=list)
    unexpected_difficulties: List[str] = field(default_factory=list)
    wrong_assumptions: List[str] = field(default_factory=list)
    discovered_constraints: List[str] = field(default_factory=list)
    evidence_files: List[str] = field(default_factory=list)
    evidence_logs: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)


@dataclass
class LearningDraft:
    """A proposed learning artifact."""
    learning_id: str
    artifact_type: LearningArtifactType
    title: str
    context: str
    evidence: List[str]
    recommendation: str
    related_intents: List[str] = field(default_factory=list)
    related_decisions: List[str] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    impact: ImpactLevel = ImpactLevel.MEDIUM
    status: str = "Proposed"
    target_artifact: Optional[str] = None  # For decision updates, pattern names, etc.


@dataclass
class ContextUpdateProposal:
    """Proposed update to a context artifact."""
    artifact_type: str  # "feature_intent", "decision", "pattern", "anti_pattern"
    artifact_path: str
    update_type: str  # "add_implementation_notes", "add_outcomes", "supersede", etc.
    proposed_content: str
    rationale: str
    status: str = "Proposed"


@dataclass
class ChangelogEntryProposal:
    """Proposed changelog entry."""
    date: str
    what_changed: str
    why_changed: str
    related_features: List[str] = field(default_factory=list)
    related_decisions: List[str] = field(default_factory=list)
    learning_artifacts: List[str] = field(default_factory=list)
    status: str = "Proposed"


@dataclass
class LearningProposal:
    """Complete learning proposal package."""
    proposal_id: str
    feature_name: str
    created_at: str
    outcome_summary: OutcomeSummary
    learning_drafts: List[LearningDraft] = field(default_factory=list)
    context_updates: List[ContextUpdateProposal] = field(default_factory=list)
    changelog_entry: Optional[ChangelogEntryProposal] = None
