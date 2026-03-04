"""Analysis domain models.

Models for brownfield repository analysis (scanning, slicing, extraction).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ConfidenceLevel(Enum):
    """Confidence level for extracted context."""
    CONFIRMED = "confirmed"
    SUSPECTED = "suspected"
    UNKNOWN = "unknown"


@dataclass
class Evidence:
    """Evidence reference for a claim."""
    file_path: str
    line_range: Optional[tuple] = None  # (start_line, end_line)
    code_snippet: Optional[str] = None
    description: str = ""


@dataclass
class ProposedArtifact:
    """A proposed context artifact from brownfield extraction."""
    artifact_type: str  # "feature_intent", "decision", "pattern", "anti_pattern"
    title: str
    content: str  # Markdown content
    confidence: ConfidenceLevel
    evidence: List[Evidence] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    proposed_at: str = ""


@dataclass
class StructuralAnalysis:
    """Structural analysis of a repository."""
    repo_root: str
    languages: Set[str] = field(default_factory=set)
    frameworks: Set[str] = field(default_factory=set)
    entry_points: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    test_presence: bool = False
    directory_structure: Dict = field(default_factory=dict)
    file_count: int = 0
    total_size: int = 0  # bytes


@dataclass
class SliceDefinition:
    """Definition of a repository slice."""
    slice_id: str
    name: str
    paths: List[str]  # Directory paths included in slice
    languages: Set[str] = field(default_factory=set)
    file_count: int = 0
    dependencies: List[str] = field(default_factory=list)  # Other slice IDs
