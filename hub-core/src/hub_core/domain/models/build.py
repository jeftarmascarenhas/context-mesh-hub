"""Build domain models.

Models for build protocol (plan, approve, execute workflow).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ApprovalStatus(Enum):
    """Approval status for build plans."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIALLY_APPROVED = "partially_approved"


@dataclass
class ImplementationStep:
    """A single step in the implementation plan."""
    step_number: int
    description: str
    target_files: List[str] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)  # e.g., "create", "modify", "validate"
    constraints: List[str] = field(default_factory=list)
    validation_checks: List[str] = field(default_factory=list)


@dataclass
class BuildPlan:
    """Structured build plan for a feature."""
    plan_id: str
    feature_name: str
    feature_path: str
    created_at: str
    implementation_steps: List[ImplementationStep] = field(default_factory=list)
    target_files: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    non_goals: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    related_decisions: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class ApprovalState:
    """Approval state for a build plan."""
    plan_id: str
    status: ApprovalStatus
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None  # User identifier (optional for v1)
    approved_scope: Optional[List[int]] = None  # Step numbers for partial approval
    rejection_feedback: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ExecutionInstruction:
    """Structured execution instruction."""
    instruction_id: str
    plan_id: str
    step_number: int
    operation: str  # "create", "modify", "delete", "validate"
    target_file: Optional[str] = None
    content: Optional[str] = None
    description: str = ""
    validation_check: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
