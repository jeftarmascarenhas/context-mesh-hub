"""Repository for BuildPlan persistence."""

from typing import List, Optional
from dataclasses import asdict

from ...domain.models.build import (
    BuildPlan,
    ApprovalState,
    ImplementationStep,
    ApprovalStatus,
)
from ...shared.errors import ArtifactNotFoundError
from .file_store import FileStore


class PlanRepository:
    """Repository for managing BuildPlan persistence.
    
    Handles serialization/deserialization and CRUD operations for build plans.
    """
    
    def __init__(self, store: FileStore):
        """Initialize repository.
        
        Args:
            store: FileStore instance for persistence.
        """
        self.store = store
    
    def save_plan(self, plan: BuildPlan) -> None:
        """Save build plan.
        
        Args:
            plan: BuildPlan to save.
        """
        data = self._plan_to_dict(plan)
        self.store.save(f"plan_{plan.plan_id}", data)
    
    def load_plan(self, plan_id: str) -> Optional[BuildPlan]:
        """Load build plan by ID.
        
        Args:
            plan_id: Plan identifier.
            
        Returns:
            BuildPlan if found, None otherwise.
        """
        data = self.store.load(f"plan_{plan_id}")
        if not data:
            return None
        
        return self._dict_to_plan(data)
    
    def get_plan(self, plan_id: str) -> BuildPlan:
        """Get build plan by ID (raises if not found).
        
        Args:
            plan_id: Plan identifier.
            
        Returns:
            BuildPlan instance.
            
        Raises:
            ArtifactNotFoundError: If plan not found.
        """
        plan = self.load_plan(plan_id)
        if not plan:
            raise ArtifactNotFoundError("BuildPlan", plan_id)
        return plan
    
    def list_plans(self) -> List[BuildPlan]:
        """List all plans.
        
        Returns:
            List of BuildPlan instances.
        """
        keys = [k for k in self.store.list_keys() if k.startswith("plan_")]
        plans = []
        
        for key in keys:
            data = self.store.load(key)
            if data:
                plans.append(self._dict_to_plan(data))
        
        return plans
    
    def delete_plan(self, plan_id: str) -> None:
        """Delete build plan.
        
        Args:
            plan_id: Plan identifier.
        """
        self.store.delete(f"plan_{plan_id}")
    
    def save_approval(self, plan_id: str, approval: ApprovalState) -> None:
        """Save approval state for a plan.
        
        Args:
            plan_id: Plan identifier.
            approval: ApprovalState to save.
        """
        data = asdict(approval)
        # Convert enum to string
        data['status'] = approval.status.value
        self.store.save(f"approval_{plan_id}", data)
    
    def load_approval(self, plan_id: str) -> Optional[ApprovalState]:
        """Load approval state for a plan.
        
        Args:
            plan_id: Plan identifier.
            
        Returns:
            ApprovalState if found, None otherwise.
        """
        data = self.store.load(f"approval_{plan_id}")
        if not data:
            return None
        
        # Convert string back to enum
        data['status'] = ApprovalStatus(data['status'])
        return ApprovalState(**data)
    
    def _plan_to_dict(self, plan: BuildPlan) -> dict:
        """Convert BuildPlan to dict for serialization."""
        data = asdict(plan)
        # No enums in BuildPlan, just nested dataclasses
        return data
    
    def _dict_to_plan(self, data: dict) -> BuildPlan:
        """Convert dict to BuildPlan."""
        # Reconstruct nested ImplementationStep objects
        steps_data = data.get('implementation_steps', [])
        steps = [ImplementationStep(**step_data) for step_data in steps_data]
        
        data['implementation_steps'] = steps
        return BuildPlan(**data)
