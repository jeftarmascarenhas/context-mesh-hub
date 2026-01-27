"""Build Protocol implementation for Plan / Approve / Execute workflow."""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum

from .loader import ContextLoader
from .bundler import ContextBundler


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


class BuildProtocol:
    """Build Protocol implementation for Plan / Approve / Execute."""
    
    def __init__(self, loader: ContextLoader, bundler: ContextBundler):
        """Initialize Build Protocol.
        
        Args:
            loader: ContextLoader instance.
            bundler: ContextBundler instance.
        """
        self.loader = loader
        self.bundler = bundler
        self._plans: Dict[str, BuildPlan] = {}
        self._approvals: Dict[str, ApprovalState] = {}
    
    def create_plan(self, feature_name: str) -> BuildPlan:
        """Create a build plan for a feature.
        
        Args:
            feature_name: Name of the feature (e.g., "hub-core").
            
        Returns:
            BuildPlan instance.
            
        Raises:
            ValueError: If feature not found.
        """
        # Get feature intent
        feature = self.loader.get_feature_intent(feature_name)
        if not feature:
            raise ValueError(f"Feature intent not found: {feature_name}")
        
        plan_id = str(uuid.uuid4())
        content = feature["content"]
        
        # Extract information from feature intent
        acceptance_criteria = self._extract_acceptance_criteria(content)
        constraints = self._extract_constraints(content)
        non_goals = self._extract_non_goals(content)
        implementation_approach = self._extract_implementation_approach(content)
        related_decisions = self._extract_decision_links(content)
        
        # Generate implementation steps
        steps = self._generate_steps(
            feature_name,
            content,
            acceptance_criteria,
            implementation_approach
        )
        
        # Identify target files from steps
        target_files = []
        for step in steps:
            target_files.extend(step.target_files)
        target_files = sorted(set(target_files))
        
        # Extract risks and assumptions
        risks = self._extract_risks(content)
        assumptions = self._extract_assumptions(content)
        
        plan = BuildPlan(
            plan_id=plan_id,
            feature_name=feature_name,
            feature_path=feature["path"],
            created_at=datetime.utcnow().isoformat(),
            implementation_steps=steps,
            target_files=target_files,
            constraints=constraints,
            non_goals=non_goals,
            risks=risks,
            assumptions=assumptions,
            related_decisions=sorted(related_decisions),
            acceptance_criteria=acceptance_criteria,
        )
        
        self._plans[plan_id] = plan
        return plan
    
    def approve_plan(
        self,
        plan_id: str,
        action: str,
        scope: Optional[List[int]] = None,
        feedback: Optional[str] = None
    ) -> ApprovalState:
        """Approve or reject a build plan.
        
        Args:
            plan_id: Plan ID to approve/reject.
            action: "approve" or "reject".
            scope: Optional list of step numbers for partial approval.
            feedback: Optional feedback message.
            
        Returns:
            ApprovalState instance.
            
        Raises:
            ValueError: If plan not found or invalid action.
        """
        if plan_id not in self._plans:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan = self._plans[plan_id]
        
        if action == "approve":
            if scope:
                # Partial approval
                status = ApprovalStatus.PARTIALLY_APPROVED
                approved_scope = scope
            else:
                # Full approval
                status = ApprovalStatus.APPROVED
                approved_scope = [step.step_number for step in plan.implementation_steps]
            
            approval = ApprovalState(
                plan_id=plan_id,
                status=status,
                approved_at=datetime.utcnow().isoformat(),
                approved_scope=approved_scope,
                notes=feedback,
            )
        elif action == "reject":
            approval = ApprovalState(
                plan_id=plan_id,
                status=ApprovalStatus.REJECTED,
                rejection_feedback=feedback or "Plan rejected",
            )
        else:
            raise ValueError(f"Invalid action: {action}. Must be 'approve' or 'reject'")
        
        self._approvals[plan_id] = approval
        return approval
    
    def generate_instructions(
        self,
        plan_id: str,
        mode: str = "instruction"
    ) -> List[ExecutionInstruction]:
        """Generate execution instructions from an approved plan.
        
        Args:
            plan_id: Plan ID to generate instructions for.
            mode: Execution mode ("instruction" or "assisted").
            
        Returns:
            List of ExecutionInstruction instances.
            
        Raises:
            ValueError: If plan not found or not approved.
        """
        if plan_id not in self._plans:
            raise ValueError(f"Plan not found: {plan_id}")
        
        approval = self._approvals.get(plan_id)
        if not approval or approval.status not in [ApprovalStatus.APPROVED, ApprovalStatus.PARTIALLY_APPROVED]:
            raise ValueError(
                f"Plan {plan_id} is not approved. Current status: "
                f"{approval.status.value if approval else 'pending'}"
            )
        
        plan = self._plans[plan_id]
        instructions = []
        
        # Determine which steps to execute
        if approval.status == ApprovalStatus.PARTIALLY_APPROVED:
            steps_to_execute = [
                step for step in plan.implementation_steps
                if step.step_number in (approval.approved_scope or [])
            ]
        else:
            steps_to_execute = plan.implementation_steps
        
        # Generate instructions for each step
        for step in steps_to_execute:
            for operation in step.operations:
                instruction = ExecutionInstruction(
                    instruction_id=str(uuid.uuid4()),
                    plan_id=plan_id,
                    step_number=step.step_number,
                    operation=operation,
                    target_file=step.target_files[0] if step.target_files else None,
                    description=step.description,
                    validation_check=step.validation_checks[0] if step.validation_checks else None,
                    constraints=step.constraints + plan.constraints,
                )
                instructions.append(instruction)
        
        return instructions
    
    def get_plan(self, plan_id: str) -> Optional[BuildPlan]:
        """Get a build plan by ID."""
        return self._plans.get(plan_id)
    
    def get_approval(self, plan_id: str) -> Optional[ApprovalState]:
        """Get approval state for a plan."""
        return self._approvals.get(plan_id)
    
    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """Extract acceptance criteria from feature intent."""
        criteria = []
        in_section = False
        current_criterion = ""
        
        for line in content.split("\n"):
            if re.match(r"^###?\s+Acceptance Criteria", line):
                in_section = True
                continue
            elif in_section and re.match(r"^###?\s+", line):
                # Next section started
                break
            elif in_section:
                # Check for checkbox items
                match = re.match(r"^-\s+\[[ x]\]\s+(.+)", line)
                if match:
                    if current_criterion:
                        criteria.append(current_criterion.strip())
                    current_criterion = match.group(1)
                elif line.strip() and current_criterion:
                    current_criterion += " " + line.strip()
        
        if current_criterion:
            criteria.append(current_criterion.strip())
        
        return criteria
    
    def _extract_constraints(self, content: str) -> List[str]:
        """Extract constraints from feature intent."""
        constraints = []
        in_section = False
        
        for line in content.split("\n"):
            if re.match(r"^###?\s+Constraints", line):
                in_section = True
                continue
            elif in_section and re.match(r"^###?\s+", line):
                break
            elif in_section:
                match = re.match(r"^-\s+\*\*(.+?)\*\*:\s*(.+)", line)
                if match:
                    constraints.append(f"{match.group(1)}: {match.group(2)}")
                elif line.strip().startswith("-"):
                    constraints.append(line.strip()[2:])
        
        return constraints
    
    def _extract_non_goals(self, content: str) -> List[str]:
        """Extract non-goals from feature intent."""
        non_goals = []
        in_section = False
        
        for line in content.split("\n"):
            if re.match(r"^###?\s+Out of Scope", line):
                in_section = True
                continue
            elif in_section and re.match(r"^###?\s+", line):
                break
            elif in_section:
                if line.strip().startswith("-"):
                    non_goals.append(line.strip()[2:])
        
        return non_goals
    
    def _extract_implementation_approach(self, content: str) -> List[str]:
        """Extract implementation approach steps."""
        approach = []
        in_section = False
        
        for line in content.split("\n"):
            if re.match(r"^###?\s+Implementation Approach", line):
                in_section = True
                continue
            elif in_section and re.match(r"^###?\s+", line):
                break
            elif in_section:
                match = re.match(r"^\d+\.\s+\*\*(.+?)\*\*", line)
                if match:
                    approach.append(match.group(1))
                elif line.strip().startswith("-"):
                    approach.append(line.strip()[2:])
        
        return approach
    
    def _extract_decision_links(self, content: str) -> Set[str]:
        """Extract decision numbers from links."""
        decision_nums = set()
        pattern = r'\[Decision:[^\]]+\]\(\.\./decisions/(\d{3})-[^\)]+\.md\)'
        matches = re.findall(pattern, content)
        decision_nums.update(matches)
        return decision_nums
    
    def _extract_risks(self, content: str) -> List[str]:
        """Extract risks from content (if mentioned)."""
        risks = []
        # Look for risk mentions in various sections
        if "risk" in content.lower() or "danger" in content.lower():
            # Simple extraction - can be enhanced
            for line in content.split("\n"):
                if "risk" in line.lower() and line.strip().startswith("-"):
                    risks.append(line.strip()[2:])
        return risks
    
    def _extract_assumptions(self, content: str) -> List[str]:
        """Extract assumptions from content (if mentioned)."""
        assumptions = []
        # Look for assumption mentions
        if "assumption" in content.lower():
            for line in content.split("\n"):
                if "assumption" in line.lower() and line.strip().startswith("-"):
                    assumptions.append(line.strip()[2:])
        return assumptions
    
    def _generate_steps(
        self,
        feature_name: str,
        content: str,
        acceptance_criteria: List[str],
        implementation_approach: List[str]
    ) -> List[ImplementationStep]:
        """Generate implementation steps from feature intent."""
        steps = []
        step_num = 1
        
        # Use implementation approach if available
        if implementation_approach:
            for approach_item in implementation_approach:
                # Infer target files from feature name and approach
                target_files = self._infer_target_files(feature_name, approach_item)
                
                step = ImplementationStep(
                    step_number=step_num,
                    description=approach_item,
                    target_files=target_files,
                    operations=["create"] if "create" in approach_item.lower() else ["modify"],
                    constraints=[],
                    validation_checks=[f"Verify {approach_item.lower()}"],
                )
                steps.append(step)
                step_num += 1
        else:
            # Fallback: create steps from acceptance criteria
            for criterion in acceptance_criteria[:5]:  # Limit to 5 steps
                step = ImplementationStep(
                    step_number=step_num,
                    description=f"Implement: {criterion}",
                    target_files=[],
                    operations=["modify"],
                    constraints=[],
                    validation_checks=[f"Verify {criterion.lower()}"],
                )
                steps.append(step)
                step_num += 1
        
        return steps
    
    def _infer_target_files(self, feature_name: str, approach_item: str) -> List[str]:
        """Infer target files from feature name and approach."""
        files = []
        
        # Common patterns
        if "setup" in approach_item.lower() or "initialize" in approach_item.lower():
            files.append(f"{feature_name}/pyproject.toml")
            files.append(f"{feature_name}/README.md")
        elif "implement" in approach_item.lower():
            # Try to infer module name
            module_name = feature_name.replace("-", "_")
            files.append(f"{feature_name}/src/{module_name}/")
        elif "test" in approach_item.lower():
            files.append(f"{feature_name}/tests/")
        
        return files
