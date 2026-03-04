"""Build Service - Plan/Approve/Execute workflow.

Pure business logic with dependency injection.
Delegates I/O to infrastructure layer (persistence).
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set
import re

from ...loader import ContextLoader
from ...bundler import ContextBundler
from ...infrastructure.parsers.markdown_parser import MarkdownParser
from ...infrastructure.parsers.extractor import BuildPlanExtractor
from ...infrastructure.persistence.plan_repository import PlanRepository
from ...shared.errors import ArtifactNotFoundError, ValidationError, PlanNotApprovedError
from ..models.build import (
    ApprovalStatus,
    ImplementationStep,
    BuildPlan,
    ApprovalState,
    ExecutionInstruction,
)


class BuildService:
    """Service for Build Protocol: Plan / Approve / Execute workflow.
    
    Orchestrates build planning, approval, and execution instruction generation.
    All state is persisted via PlanRepository (file-based).
    """
    
    def __init__(
        self,
        loader: ContextLoader,
        bundler: ContextBundler,
        plan_repository: PlanRepository,
        parser: MarkdownParser,
        extractor: BuildPlanExtractor,
    ):
        """Initialize build service with dependencies.
        
        Args:
            loader: ContextLoader for accessing artifacts
            bundler: ContextBundler for context bundling
            plan_repository: PlanRepository for persisting plans/approvals
            parser: MarkdownParser for extracting markdown sections
            extractor: BuildPlanExtractor for extracting build-specific info
        """
        self.loader = loader
        self.bundler = bundler
        self.plan_repo = plan_repository
        self.parser = parser
        self.extractor = extractor
    
    # ========================================================================
    # PLAN OPERATIONS
    # ========================================================================
    
    def create_plan(self, feature_name: str) -> BuildPlan:
        """Create a build plan for a feature.
        
        Args:
            feature_name: Feature ID (F001) or slug
        
        Returns:
            BuildPlan instance
            
        Raises:
            ArtifactNotFoundError: If feature not found
        """
        # Get feature intent
        feature = self.loader.get_feature_intent(feature_name)
        if not feature:
            raise ArtifactNotFoundError(
                f"Feature intent not found: {feature_name}",
                artifact_type="feature",
                artifact_name=feature_name
            )
        
        plan_id = str(uuid.uuid4())
        content = feature["content"]
        
        # Extract information using parser and extractor
        acceptance_criteria = self.parser.extract_list_items(content, "Acceptance Criteria")
        constraints = self.extractor.extract_constraints(content)
        non_goals = self.extractor.extract_non_goals(content)
        related_decisions = self.parser.extract_decision_links(content)
        risks = self.extractor.extract_risks(content)
        
        # Extract implementation approach
        implementation_approach = self._extract_implementation_approach(content)
        
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
        
        # Create build plan
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
            assumptions=[],  # Can be extracted if present in feature
            related_decisions=sorted(related_decisions),
            acceptance_criteria=acceptance_criteria,
        )
        
        # Persist plan
        self.plan_repo.save_plan(plan)
        
        return plan
    
    def get_plan(self, plan_id: str) -> BuildPlan:
        """Get a build plan by ID.
        
        Args:
            plan_id: Plan ID
        
        Returns:
            BuildPlan instance
            
        Raises:
            ArtifactNotFoundError: If plan not found
        """
        plan = self.plan_repo.get_plan(plan_id)
        if not plan:
            raise ArtifactNotFoundError(
                f"Build plan not found: {plan_id}",
                artifact_type="build_plan",
                artifact_name=plan_id
            )
        return plan
    
    def list_plans(self) -> List[BuildPlan]:
        """List all build plans.
        
        Returns:
            List of BuildPlan instances
        """
        return self.plan_repo.list_plans()
    
    def delete_plan(self, plan_id: str) -> None:
        """Delete a build plan.
        
        Args:
            plan_id: Plan ID
            
        Raises:
            ArtifactNotFoundError: If plan not found
        """
        plan = self.plan_repo.get_plan(plan_id)
        if not plan:
            raise ArtifactNotFoundError(
                f"Build plan not found: {plan_id}",
                artifact_type="build_plan",
                artifact_name=plan_id
            )
        self.plan_repo.delete_plan(plan_id)
    
    # ========================================================================
    # APPROVAL OPERATIONS
    # ========================================================================
    
    def approve_plan(
        self,
        plan_id: str,
        action: str,
        scope: Optional[List[int]] = None,
        feedback: Optional[str] = None,
    ) -> ApprovalState:
        """Approve or reject a build plan.
        
        Args:
            plan_id: Plan ID to approve/reject
            action: "approve" or "reject"
            scope: Optional list of step numbers for partial approval
            feedback: Optional feedback message
        
        Returns:
            ApprovalState instance
            
        Raises:
            ArtifactNotFoundError: If plan not found
            ValidationError: If invalid action
        """
        # Get plan
        plan = self.get_plan(plan_id)
        
        # Validate action
        if action not in ["approve", "reject"]:
            raise ValidationError(
                f"Invalid action: {action}. Must be 'approve' or 'reject'",
                details={"valid_actions": ["approve", "reject"]}
            )
        
        # Create approval state
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
        else:  # reject
            approval = ApprovalState(
                plan_id=plan_id,
                status=ApprovalStatus.REJECTED,
                rejection_feedback=feedback or "Plan rejected",
            )
        
        # Persist approval
        self.plan_repo.save_approval(approval)
        
        return approval
    
    def get_approval(self, plan_id: str) -> Optional[ApprovalState]:
        """Get approval state for a plan.
        
        Args:
            plan_id: Plan ID
        
        Returns:
            ApprovalState instance or None if not approved yet
        """
        return self.plan_repo.load_approval(plan_id)
    
    # ========================================================================
    # EXECUTION OPERATIONS
    # ========================================================================
    
    def generate_instructions(
        self,
        plan_id: str,
        mode: str = "instruction",
    ) -> List[ExecutionInstruction]:
        """Generate execution instructions from an approved plan.
        
        Args:
            plan_id: Plan ID to generate instructions for
            mode: Execution mode ("instruction" or "assisted")
        
        Returns:
            List of ExecutionInstruction instances
            
        Raises:
            ArtifactNotFoundError: If plan not found
            PlanNotApprovedError: If plan not approved
        """
        # Get plan
        plan = self.get_plan(plan_id)
        
        # Get approval
        approval = self.get_approval(plan_id)
        if not approval or approval.status not in [
            ApprovalStatus.APPROVED,
            ApprovalStatus.PARTIALLY_APPROVED
        ]:
            raise PlanNotApprovedError(
                f"Plan {plan_id} is not approved",
                plan_id=plan_id,
                current_status=approval.status.value if approval else "pending"
            )
        
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
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _extract_implementation_approach(self, content: str) -> List[str]:
        """Extract implementation approach steps from feature content.
        
        Args:
            content: Feature markdown content
        
        Returns:
            List of approach steps
        """
        approach = []
        in_section = False
        
        for line in content.split("\n"):
            if re.match(r"^###?\s+Implementation Approach", line):
                in_section = True
                continue
            elif in_section and re.match(r"^###?\s+", line):
                break
            elif in_section:
                # Match numbered steps with bold titles
                match = re.match(r"^\d+\.\s+\*\*(.+?)\*\*", line)
                if match:
                    approach.append(match.group(1))
                elif line.strip().startswith("-"):
                    approach.append(line.strip()[2:])
        
        return approach
    
    def _generate_steps(
        self,
        feature_name: str,
        content: str,
        acceptance_criteria: List[str],
        implementation_approach: List[str],
    ) -> List[ImplementationStep]:
        """Generate implementation steps from feature intent.
        
        Args:
            feature_name: Feature ID or name
            content: Feature markdown content
            acceptance_criteria: List of acceptance criteria
            implementation_approach: List of implementation steps
        
        Returns:
            List of ImplementationStep instances
        """
        steps = []
        step_num = 1
        
        # Use implementation approach if available
        if implementation_approach:
            for approach_item in implementation_approach:
                # Infer target files from feature name and approach
                target_files = self._infer_target_files(feature_name, approach_item)
                
                # Infer operations from approach text
                operations = []
                if "create" in approach_item.lower() or "add" in approach_item.lower():
                    operations.append("create")
                if "modify" in approach_item.lower() or "update" in approach_item.lower():
                    operations.append("modify")
                if "test" in approach_item.lower() or "validate" in approach_item.lower():
                    operations.append("validate")
                
                # Default to modify if no operations found
                if not operations:
                    operations = ["modify"]
                
                step = ImplementationStep(
                    step_number=step_num,
                    description=approach_item,
                    target_files=target_files,
                    operations=operations,
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
        """Infer target files from feature name and approach.
        
        Args:
            feature_name: Feature ID or name
            approach_item: Implementation approach step
        
        Returns:
            List of target file paths
        """
        files = []
        
        # Common patterns
        if "setup" in approach_item.lower() or "initialize" in approach_item.lower():
            files.append(f"{feature_name}/pyproject.toml")
            files.append(f"{feature_name}/README.md")
        elif "implement" in approach_item.lower() or "create" in approach_item.lower():
            # Try to infer module name
            module_name = feature_name.replace("-", "_")
            files.append(f"{feature_name}/src/{module_name}/")
        elif "test" in approach_item.lower():
            files.append(f"{feature_name}/tests/")
        elif "document" in approach_item.lower():
            files.append(f"{feature_name}/README.md")
            files.append(f"{feature_name}/docs/")
        
        return files
